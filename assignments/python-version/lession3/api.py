"""
FastAPI Server - HTTP API cho LangGraph agent
"""
import os
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langgraph.types import Command
from agent import create_agent_graph, extract_text
from db_setup import get_checkpointer

# Load environment variables
load_dotenv()


# Request/Response models
class AgentRequest(BaseModel):
    """Request model cho agent endpoint"""
    task: str
    thread_id: Optional[str] = "default"  # Session ID cho checkpointing
    max_turns: Optional[int] = 10


class AgentResponse(BaseModel):
    """Response model cho agent endpoint"""
    result: str
    turns: int
    status: str
    needs_approval: bool = False
    approval_message: Optional[str] = None
    pending_tool: Optional[dict] = None


class ApprovalRequest(BaseModel):
    """Request model cho approval endpoint"""
    thread_id: str
    approved: bool  # True = approve, False = reject
    reason: Optional[str] = None


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management cho FastAPI app"""
    # Startup
    print("🚀 Starting FastAPI server with LangGraph agent...")
    yield
    # Shutdown
    print("👋 Shutting down FastAPI server...")


# Initialize FastAPI app
app = FastAPI(
    title="LangGraph Agent API",
    description="FastAPI server với LangGraph agent integration",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "LangGraph Agent API is running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    api_key_set = bool(os.getenv("ANTHROPIC_API_KEY"))
    return {
        "status": "healthy" if api_key_set else "degraded",
        "api_key_configured": api_key_set,
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    }


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent_endpoint(request: AgentRequest):
    """
    Chạy agent với task đã cho (blocking)

    Args:
        request: AgentRequest chứa task, thread_id và config

    Returns:
        AgentResponse với kết quả hoặc approval request
    """
    try:
        # Get checkpointer và create agent graph
        checkpointer = get_checkpointer()
        graph = create_agent_graph(checkpointer=checkpointer)

        # Config với thread_id
        config = {"configurable": {"thread_id": request.thread_id}}

        # Check if checkpoint exists
        try:
            existing_state = graph.get_state(config)
            has_checkpoint = bool(existing_state.values)
        except:
            has_checkpoint = False

        # Prepare input for stream
        if has_checkpoint:
            # Resume from checkpoint - update with new message
            graph.update_state(
                config,
                {
                    "task": request.task,
                    "messages": [HumanMessage(content=request.task)],
                    "status": "running",
                    "verification_passed": False,
                }
            )
            stream_input = None  # Continue from checkpoint
        else:
            # New conversation - full initial state
            stream_input = {
                "task": request.task,
                "messages": [HumanMessage(content=request.task)],
                "tool_results": [],
                "plan": None,
                "iteration": 0,
                "status": "running",
                "verification_passed": False,
                "error_message": None,
                "retry_count": 0,
                "pending_tool_call": None,
                "approval_message": None,
            }

        # Use stream mode để detect interrupts properly
        final_state = None
        interrupted = False
        interrupt_value = None

        for chunk in graph.stream(stream_input, config=config):
            # Check for __interrupt__ event
            if "__interrupt__" in chunk:
                interrupted = True
                interrupt_tuple = chunk["__interrupt__"]
                if interrupt_tuple and len(interrupt_tuple) > 0:
                    interrupt_value = interrupt_tuple[0].value
                break
            # Update final_state with latest chunk
            for node_name, node_data in chunk.items():
                if node_name != "__interrupt__":
                    final_state = node_data

        # If interrupted, return approval request
        if interrupted and interrupt_value:
            # Get current state for iteration count
            current_state = graph.get_state(config)
            return AgentResponse(
                result="Waiting for approval",
                turns=current_state.values.get("iteration", 0),
                status="needs_approval",
                needs_approval=True,
                approval_message=interrupt_value.get("message"),
                pending_tool=interrupt_value
            )

        # Get final state if not already set
        if final_state is None:
            current_state = graph.get_state(config)
            final_state = current_state.values

        # Extract result
        result = extract_text(final_state["messages"][-1])

        return AgentResponse(
            result=result,
            turns=final_state.get("iteration", 0),
            status=final_state.get("status", "completed"),
            needs_approval=False
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/stream")
async def stream_agent_endpoint(request: AgentRequest):
    """
    Stream agent execution (SSE)

    Args:
        request: AgentRequest chứa task, thread_id và config

    Returns:
        StreamingResponse với server-sent events
    """
    async def event_generator():
        try:
            # Get checkpointer và create agent graph
            checkpointer = get_checkpointer()
            graph = create_agent_graph(checkpointer=checkpointer)

            # Config với thread_id
            config = {"configurable": {"thread_id": request.thread_id}}

            # Initial state - phải khớp với AgentState
            initial_state = {
                "task": request.task,
                "messages": [HumanMessage(content=request.task)],
                "tool_results": [],
                "plan": None,
                "iteration": 0,
                "status": "running",
                "verification_passed": False,
                "error_message": None,
                "retry_count": 0,
            }

            # Stream events
            yield f"data: {{'event': 'start', 'task': '{request.task}', 'thread_id': '{request.thread_id}'}}\n\n"

            # Run graph with streaming
            for chunk in graph.stream(initial_state, config=config, stream_mode="updates"):
                for node_name, node_update in chunk.items():
                    iteration = node_update.get("iteration", 0)

                    # Send node update
                    yield f"data: {{'event': 'node', 'name': '{node_name}', 'iteration': {iteration}}}\n\n"

                    # Check for messages
                    if "messages" in node_update:
                        messages = node_update["messages"]
                        for message in messages:
                            if isinstance(message, AIMessage):
                                if message.content:
                                    content = str(message.content).replace("'", "\\'")[:200]
                                    yield f"data: {{'event': 'message', 'content': '{content}'}}\n\n"

                                if hasattr(message, "tool_calls") and message.tool_calls:
                                    for tool_call in message.tool_calls:
                                        tool_name = tool_call.get("name", "unknown")
                                        yield f"data: {{'event': 'tool_call', 'tool': '{tool_name}'}}\n\n"

                            elif isinstance(message, ToolMessage):
                                result = str(message.content)[:100].replace("'", "\\'")
                                yield f"data: {{'event': 'tool_result', 'result': '{result}...'}}\n\n"

            yield f"data: {{'event': 'done'}}\n\n"

        except Exception as e:
            yield f"data: {{'event': 'error', 'message': '{str(e)}'}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.post("/agent/approve")
async def approve_agent_action(request: ApprovalRequest):
    """
    Approve hoặc reject pending tool execution

    Args:
        request: ApprovalRequest với thread_id và approved status

    Returns:
        Updated status và continuation result
    """
    try:
        # Get checkpointer và graph
        checkpointer = get_checkpointer()
        graph = create_agent_graph(checkpointer=checkpointer)

        # Config với thread_id
        config = {"configurable": {"thread_id": request.thread_id}}

        # Get current state
        current_state = graph.get_state(config)

        if not current_state.values:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Check if waiting for approval - look for interrupts in tasks
        has_interrupt = False
        if current_state.tasks:
            for task in current_state.tasks:
                if hasattr(task, 'interrupts') and task.interrupts:
                    has_interrupt = True
                    break

        if not has_interrupt:
            raise HTTPException(
                status_code=400,
                detail="Thread is not waiting for approval"
            )

        if request.approved:
            # Approve: use Command to resume with approval
            approval_data = {"approved": True}

            # Resume với Command
            final_state = graph.invoke(
                Command(resume=approval_data),
                config=config
            )

            # Check if completed or needs another approval
            if "__interrupt__" in final_state.get("tasks", [{}])[0] if final_state.get("tasks") else {}:
                interrupt_value = final_state["tasks"][0]["__interrupt__"][0].value
                return {
                    "status": "needs_approval",
                    "message": "Another approval required",
                    "approval_message": interrupt_value.get("message"),
                    "pending_tool": interrupt_value
                }

            # Extract result
            result = extract_text(final_state["messages"][-1])
            return {
                "status": "completed",
                "result": result,
                "turns": final_state.get("iteration", 0)
            }
        else:
            # Reject: resume with rejection
            rejection_msg = request.reason or "Tool execution rejected by admin"
            rejection_data = {"approved": False, "reason": rejection_msg}

            final_state = graph.invoke(
                Command(resume=rejection_data),
                config=config
            )

            return {
                "status": "rejected",
                "message": rejection_msg
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
