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
from agent import create_agent_graph, extract_text

# Load environment variables
load_dotenv()


# Request/Response models
class AgentRequest(BaseModel):
    """Request model cho agent endpoint"""
    task: str
    max_turns: Optional[int] = 10


class AgentResponse(BaseModel):
    """Response model cho agent endpoint"""
    result: str
    turns: int
    status: str


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
        request: AgentRequest chứa task và config

    Returns:
        AgentResponse với kết quả
    """
    try:
        # Create agent graph
        graph = create_agent_graph()

        # Initial state - phải khớp với AgentState
        initial_state = {
            "task": request.task,
            "messages": [HumanMessage(content=request.task)],
            "tool_results": [],
            "plan": None,
            "iteration": 0,
            "status": "running",
            "verification_passed": False,
            "error_message": None
        }

        # Run graph
        final_state = graph.invoke(initial_state)

        # Extract result
        result = extract_text(final_state["messages"][-1])

        return AgentResponse(
            result=result,
            turns=final_state.get("iteration", 0),
            status=final_state.get("status", "completed")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/stream")
async def stream_agent_endpoint(request: AgentRequest):
    """
    Stream agent execution (SSE)

    Args:
        request: AgentRequest chứa task và config

    Returns:
        StreamingResponse với server-sent events
    """
    async def event_generator():
        try:
            # Create agent graph
            graph = create_agent_graph()

            # Initial state - phải khớp với AgentState
            initial_state = {
                "task": request.task,
                "messages": [HumanMessage(content=request.task)],
                "tool_results": [],
                "plan": None,
                "iteration": 0,
                "status": "running",
                "verification_passed": False,
                "error_message": None
            }

            # Stream events
            yield f"data: {{'event': 'start', 'task': '{request.task}'}}\n\n"

            # Run graph with streaming
            for chunk in graph.stream(initial_state, stream_mode="updates"):
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
