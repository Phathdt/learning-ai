"""
LangGraph Agent - Core logic với logging support
"""

import json
import subprocess
from typing import TypedDict, Annotated, Literal
from operator import add

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, ToolMessage

# Import LLM setup
from llm_setup import create_llm, get_llm_with_tools

# Import tools
from tools import run_shell_tool, query_db, list_tables


# LangGraph State
class AgentState(TypedDict):
    """State cho agent graph"""

    # === Input ===
    task: str  # User request, không đổi

    # === Conversation ===
    messages: Annotated[list, add_messages]  # LLM conversation, dùng add để nối

    # === Intermediate results ===
    tool_results: Annotated[list[dict], add]  # Tool outputs, dùng để debug
    plan: str | None  # Plan hiện tại, overwrite mỗi lần replan

    # === Control flow ===
    iteration: int  # Đếm số vòng, dùng cho max_iterations
    status: Literal["running", "success", "failed", "needs_approval"]

    # === Verification ===
    verification_passed: bool  # Kết quả verifier
    error_message: str | None  # Lỗi gần nhất, để retry có context


# Configuration
MAX_ITERATIONS = 10


# Node functions
def planner_node(state: AgentState) -> dict:
    """
    Node planner: sinh plan hoặc replan nếu verify fail
    """
    task = state["task"]
    error_message = state.get("error_message")
    iteration = state.get("iteration", 0)

    print(f"\n=== Planning (iteration {iteration}) ===")

    # Build prompt for planning
    if error_message:
        prompt = f"Task failed: {error_message}\n\nOriginal task: {task}\n\nCreate a new plan to fix this."
    else:
        prompt = f"Task: {task}\n\nCreate a step-by-step plan to accomplish this task."

    llm = create_llm()
    response = invoke_llm_with_logging(llm, HumanMessage(content=prompt), "Planner")
    plan = extract_text(response)

    print(f"Plan: {plan[:200]}...")

    return {"plan": plan, "status": "running"}


def agent_node(state: AgentState) -> dict:
    """
    Node chính: gọi LLM với tools dựa trên plan
    """
    messages = state["messages"]
    plan = state.get("plan")
    iteration = state.get("iteration", 0)

    print(f"\n=== Turn {iteration} - Calling LLM ===")

    # Add plan context to messages if this is first agent call
    if plan and len(messages) == 1:  # Only user task
        plan_message = HumanMessage(
            content=f"Plan to follow:\n{plan}\n\nNow execute the next step."
        )
        messages = [messages[0], plan_message]

    llm_with_tools = get_llm_with_tools([run_shell_tool, query_db, list_tables])
    response = invoke_llm_with_logging(llm_with_tools, messages, "Agent")

    return {"messages": [response], "iteration": iteration + 1, "status": "running"}


def tool_node(state: AgentState) -> dict:
    """
    Node thực thi tools (với validation và permission check)
    """
    messages = state["messages"]
    last_message = messages[-1]

    tool_results = []
    tool_outputs = []

    for tool_call in last_message.tool_calls:
        print(f"  Executing: {tool_call['name']}")

        try:
            # Execute tool
            if tool_call["name"] == "run_shell_tool":
                result = run_shell_tool(**tool_call["args"])
            elif tool_call["name"] == "query_db":
                result = query_db(**tool_call["args"])
            elif tool_call["name"] == "list_tables":
                result = list_tables(**tool_call["args"])
            else:
                result = f"ERROR: Unknown tool {tool_call['name']}"

            # Create tool message
            tool_message = ToolMessage(content=result, tool_call_id=tool_call["id"])
            tool_results.append(tool_message)
            tool_outputs.append({"tool": tool_call["name"], "result": result})

            # Log tool result
            print_json(serialize_message(tool_message), "    Tool Result:")

        except Exception as e:
            error_msg = f"ERROR executing {tool_call['name']}: {str(e)}"
            tool_message = ToolMessage(content=error_msg, tool_call_id=tool_call["id"])
            tool_results.append(tool_message)
            tool_outputs.append({"tool": tool_call["name"], "error": str(e)})
            print(f"    ERROR: {str(e)}")

    return {"messages": tool_results, "tool_results": tool_outputs, "status": "running"}


def verifier_node(state: AgentState) -> dict:
    """
    Node verifier: kiểm tra xem task đã hoàn thành chưa
    """
    messages = state["messages"]
    task = state["task"]
    iteration = state.get("iteration", 0)

    print(f"\n=== Verifying (iteration {iteration}) ===")

    # Check if last message has tool calls (not complete yet)
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        print("Status: Still has pending tool calls")
        return {"verification_passed": False, "status": "running"}

    # Extract final response
    final_response = extract_text(last_message)

    # Simple verification: check if response contains actual content
    if len(final_response.strip()) < 10:
        print("Status: Response too short")
        return {
            "verification_passed": False,
            "status": "running",
            "error_message": "Response is too short or empty",
        }

    # Check for error indicators
    if "ERROR" in final_response or "failed" in final_response.lower():
        print("Status: Error detected in response")
        return {
            "verification_passed": False,
            "status": "failed",
            "error_message": final_response,
        }

    print("Status: Task completed successfully")
    return {"verification_passed": True, "status": "success"}


# Routing functions
def should_continue(state: AgentState) -> Literal["tools", "verifier"]:
    """
    Routing sau agent node: có tool calls thì execute, không thì verify
    """
    messages = state["messages"]
    last_message = messages[-1]

    # Has tool calls: execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # No tool calls: go to verifier
    return "verifier"


def route_after_verify(state: AgentState) -> Literal["planner", "agent", "end"]:
    """
    Routing sau verifier: task xong? replan? tiếp tục?
    """
    iteration = state.get("iteration", 0)
    verification_passed = state.get("verification_passed", False)
    status = state.get("status", "running")

    # Budget stop: max iterations
    if iteration >= MAX_ITERATIONS:
        print(f"Max iterations ({MAX_ITERATIONS}) reached")
        return "end"

    # Task completed successfully
    if verification_passed and status == "success":
        return "end"

    # Task failed: need replan
    if status == "failed" or state.get("error_message"):
        return "planner"

    # Continue with agent
    return "agent"


# Build graph
def create_agent_graph(checkpointer=None):
    """
    Tạo LangGraph cho agent loop với planner và verifier

    Flow:
    planner → agent → [tools] → verifier → {planner|agent|END}
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("verifier", verifier_node)

    # Add edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "agent")

    # Conditional: agent → tools or verifier
    workflow.add_conditional_edges(
        "agent", should_continue, {"tools": "tools", "verifier": "verifier"}
    )

    workflow.add_edge("tools", "agent")

    # Conditional: verifier → planner, agent, or END
    workflow.add_conditional_edges(
        "verifier",
        route_after_verify,
        {"planner": "planner", "agent": "agent", "end": END},
    )

    return workflow.compile(checkpointer=checkpointer)


def extract_text(message) -> str:
    """Trích xuất text từ message"""
    if hasattr(message, "content"):
        if isinstance(message.content, str):
            return message.content
        elif isinstance(message.content, list):
            texts = [
                block.get("text", "")
                for block in message.content
                if isinstance(block, dict)
            ]
            return " ".join(texts)
    return ""


def run_agent(task: str, verbose: bool = True) -> str:
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
        "task": task,
        "messages": [HumanMessage(content=task)],
        "tool_results": [],
        "plan": None,
        "iteration": 0,
        "status": "running",
        "verification_passed": False,
        "error_message": None,
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


def invoke_llm_with_logging(llm, messages, label: str = "LLM"):
    """
    Helper: invoke LLM và log request/response với jq

    Args:
        llm: LLM instance
        messages: List of messages hoặc single message
        label: Label cho logging (default: "LLM")

    Returns:
        Response từ LLM
    """
    # Normalize to list
    if not isinstance(messages, list):
        messages = [messages]

    # Log request
    print_json([serialize_message(msg) for msg in messages], f"Request to {label}:")

    # Invoke LLM
    response = llm.invoke(messages)

    # Log response
    print_json(serialize_message(response), f"Response from {label}:")

    return response


def run_agent_with_logging(task: str) -> str:
    """
    Chạy agent với logging (nodes tự log qua invoke_llm_with_logging)
    """
    graph = create_agent_graph()

    initial_state = {
        "task": task,
        "messages": [HumanMessage(content=task)],
        "tool_results": [],
        "plan": None,
        "iteration": 0,
        "status": "running",
        "verification_passed": False,
        "error_message": None,
    }

    print(f"\n{'=' * 60}")
    print(f"TASK: {task}")
    print(f"{'=' * 60}")

    # Invoke graph (nodes sẽ tự log)
    final_state = graph.invoke(initial_state)

    # Extract final answer
    result = extract_text(final_state["messages"][-1])
    return result
