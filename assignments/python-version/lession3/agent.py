"""
LangGraph Agent - Core logic với logging support
"""
import json
import os
import subprocess
from typing import TypedDict, Annotated, Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, ToolMessage

# Import tools
from tools import run_shell_tool

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = os.getenv("ANTHROPIC_API_URL")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")


def get_llm_with_tools():
    """
    Tạo LLM instance với tools binding

    Returns:
        ChatAnthropic instance đã bind tools
    """
    llm = ChatAnthropic(
        model_name=MODEL,
        api_key=API_KEY,
        base_url=API_URL,
        timeout=60.0,
        stop=None
    )

    # Bind tools to LLM
    tools = [run_shell_tool]
    return llm.bind_tools(tools)


# LangGraph State
class AgentState(TypedDict):
    """State cho agent graph"""
    messages: Annotated[list, add_messages]
    turn_count: int


# Node functions
def agent_node(state: AgentState) -> AgentState:
    """
    Node chính: gọi LLM với tools
    """
    messages = state["messages"]
    turn_count = state.get("turn_count", 0)

    print(f"\n=== Turn {turn_count} - Calling LLM ===")

    # Log request (all messages sent to LLM)
    print_json([serialize_message(msg) for msg in messages], "Request to LLM:")

    llm_with_tools = get_llm_with_tools()
    response = llm_with_tools.invoke(messages)

    # Log response
    print_json(serialize_message(response), "Response from LLM:")

    return {
        "messages": [response],
        "turn_count": turn_count + 1
    }


def tool_node(state: AgentState) -> AgentState:
    """
    Node thực thi tools
    """
    messages = state["messages"]
    last_message = messages[-1]

    tool_results = []
    for tool_call in last_message.tool_calls:
        print(f"  Executing: {tool_call['name']}")

        # Execute tool
        if tool_call["name"] == "run_shell_tool":
            result = run_shell_tool(**tool_call["args"])
        else:
            result = f"ERROR: Unknown tool {tool_call['name']}"

        # Create tool message
        tool_message = ToolMessage(
            content=result,
            tool_call_id=tool_call["id"]
        )
        tool_results.append(tool_message)

        # Log tool result
        print_json(serialize_message(tool_message), "    Tool Result:")

    return {"messages": tool_results, "turn_count": state.get("turn_count", 0)}


# Routing function
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    """
    Quyết định có tiếp tục loop hay kết thúc
    """
    messages = state["messages"]
    last_message = messages[-1]
    turn_count = state.get("turn_count", 0)

    # Budget stop: max turns
    if turn_count >= 10:
        return "end"

    # Natural stop: no tool calls
    if not last_message.tool_calls:
        return "end"

    # Continue: has tool calls
    return "tools"


# Build graph
def create_agent_graph():
    """
    Tạo LangGraph cho agent loop
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()


def extract_text(message) -> str:
    """Trích xuất text từ message"""
    if hasattr(message, "content"):
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            texts = [block.get("text", "") for block in message.content if isinstance(block, dict)]
            return " ".join(texts)
    return ""


def run_agent(task: str, verbose: bool = False) -> str:
    """
    Chạy agent với task đã cho

    Args:
        task: Nhiệm vụ cho agent
        verbose: Nếu True, in ra logging với jq

    Returns:
        Kết quả cuối cùng từ agent
    """
    if verbose:
        return run_agent_with_logging(task)

    graph = create_agent_graph()

    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=task)],
        "turn_count": 0
    }

    final_state = graph.invoke(initial_state)

    # Extract final answer
    return extract_text(final_state["messages"][-1])


# ============================================================================
# Logging utilities (cho verbose mode)
# ============================================================================

def print_json(data, label: str = ""):
    """Print JSON với jq nếu có, fallback về json.dumps"""
    json_str = json.dumps(data, ensure_ascii=False)

    try:
        result = subprocess.run(
            ["jq", "-C", "."],
            input=json_str,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            if label:
                print(f"\n{label}")
            print(result.stdout)
            return
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback to Python json
    if label:
        print(f"\n{label}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def serialize_message(msg):
    """Serialize message để print với jq"""
    if hasattr(msg, "type"):
        result = {"role": msg.type, "content": msg.content}
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            result["tool_calls"] = msg.tool_calls
        if hasattr(msg, "tool_call_id"):
            result["tool_call_id"] = msg.tool_call_id
        return result
    return {"content": str(msg)}


def run_agent_with_logging(task: str) -> str:
    """
    Chạy agent với logging request/response cho mỗi LLM call
    """
    graph = create_agent_graph()

    initial_state = {"messages": [HumanMessage(content=task)], "turn_count": 0}

    print(f"\n{'=' * 60}")
    print(f"TASK: {task}")
    print(f"{'=' * 60}")

    turn = 0
    all_messages = initial_state["messages"][:]

    # Stream updates từ graph
    for chunk in graph.stream(initial_state, stream_mode="updates"):
        for node_name, node_update in chunk.items():
            messages = node_update.get("messages", [])

            if not messages:
                continue

            # Log dựa trên node
            if node_name == "agent":
                # Agent node: log request (trước khi gọi) và response
                print(f"\n=== Turn {turn} - Calling LLM ===")

                # Request: tất cả messages hiện có
                print_json(
                    [serialize_message(msg) for msg in all_messages], "Request to LLM:"
                )

                # Response: AI message với tool_calls
                ai_message = messages[0]
                print_json(serialize_message(ai_message), "Response from LLM:")

                all_messages.append(ai_message)

            elif node_name == "tools":
                # Tool node: log tool results
                for tool_msg in messages:
                    print_json(serialize_message(tool_msg), "  Tool Result:")
                    all_messages.append(tool_msg)

            turn += 1

    # Get final answer
    final_state = graph.invoke(initial_state)
    result = extract_text(final_state["messages"][-1])

    return result
