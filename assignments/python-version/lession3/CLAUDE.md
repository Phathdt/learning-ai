# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Assignment Lesson 3** từ khóa học Agent Engineering - xây dựng LangGraph Agent với FastAPI REST API.

Đây là bài tập thực hành về agent loop với **Planner → Agent → Tools → Verifier** pattern, kết hợp state management và streaming support.

**Tech stack:** LangGraph, FastAPI, Uvicorn, langchain-anthropic, Claude API

**Related context:** Đây là phần của project học tập lớn hơn về Agent Engineering. Xem `/Users/phathdt/Documents/Dev/learning-ai/CLAUDE.md` để hiểu toàn bộ curriculum.

## Architecture

Cấu trúc 3-layer với LangGraph state machine ở core:

```
FastAPI (api.py) → LangGraph Agent (agent.py) → Claude API
                       ↓
                   Shell Tools (tools/shell.py)
```

### Agent Loop Flow

```
User Task → Planner → Agent → [Tools] → Verifier → {END | replan | continue}
```

**Nodes:**
- `planner_node`: Tạo plan hoặc replan khi có error
- `agent_node`: Gọi LLM với tools dựa trên plan
- `tool_node`: Execute tools với validation và error handling
- `verifier_node`: Kiểm tra task completion và detect errors

**Routing logic:**
- `should_continue`: agent → tools (nếu có tool_calls) hoặc verifier
- `route_after_verify`: verifier → planner (replan) | agent (continue) | END

**Termination conditions:**
- Natural stop: Model không gọi thêm tool và verifier pass
- Budget stop: Đạt MAX_ITERATIONS (default: 10)
- Error stop: Verifier detect error và trigger replan

### State Management

```python
class AgentState(TypedDict):
    task: str                                    # User request (immutable)
    messages: Annotated[list, add_messages]      # LLM conversation (append-only)
    tool_results: Annotated[list[dict], add]     # Tool outputs (for debugging)
    plan: str | None                             # Current plan (overwrite on replan)
    iteration: int                               # Loop counter (for max_iterations)
    status: Literal["running", "success", "failed", "needs_approval"]
    verification_passed: bool                    # Verifier result
    error_message: str | None                    # Last error (for replan context)
```

**Key points:**
- `messages` dùng `add_messages` reducer → tự động nối messages
- `plan` overwrite mỗi lần replan (không dùng add)
- `iteration` track số vòng loop để enforce budget limit
- `error_message` giữ context cho planner khi replan

## Development Commands

### Start Development Server

```bash
# Start FastAPI server với auto-reload
uv run python main.py

# Server chạy tại http://localhost:8000
# Logs hiển thị màu với jq (nếu có)
```

### Run Tests

```bash
# Run all 10 test cases
./test-api.sh

# Cần server đang chạy trước khi test
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/health

# Run agent (blocking)
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List all Python files"}' | jq

# Stream agent (SSE)
curl -N http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"task": "Count Python files"}'
```

### Dependencies

```bash
# Install/update dependencies
uv sync

# Requires Python 3.11+
```

## Code Organization

### Entry Points

- `main.py` - Server entry point, chạy Uvicorn
- `api.py` - FastAPI app với 2 endpoints: `/agent/run` (blocking), `/agent/stream` (SSE)
- `agent.py` - LangGraph core logic với 4 nodes và routing functions

### Core Components

**agent.py:**
- `AgentState` - TypedDict cho state schema
- `create_agent_graph()` - Build và compile LangGraph workflow
- `planner_node()`, `agent_node()`, `tool_node()`, `verifier_node()` - Graph nodes
- `should_continue()`, `route_after_verify()` - Conditional routing functions
- `run_agent()` - High-level API để chạy agent với task string

**api.py:**
- `AgentRequest`, `AgentResponse` - Pydantic models
- `POST /agent/run` - Blocking execution, trả về final result
- `POST /agent/stream` - SSE streaming với real-time updates
- `GET /health` - Health check với API key validation

**llm_setup.py:**
- `get_llm_with_tools()` - Tạo ChatAnthropic instance và bind tools
- Load config từ `.env`: `ANTHROPIC_API_KEY`, `ANTHROPIC_API_URL`, `ANTHROPIC_MODEL`

**tools/shell.py:**
- `run_shell_tool()` - Execute shell commands với guardrails
- Whitelist: `ls`, `cat`, `grep`, `wc`, `head`, `find`, `pwd` (read-only)
- Auto-filter output để exclude `.venv`, `__pycache__`, `.git`, `node_modules`
- Timeout: 10s, output limit: 4000 chars

### File Structure

```
lession3/
├── main.py              # Entry point
├── api.py               # FastAPI REST endpoints
├── agent.py             # LangGraph agent loop (core logic)
├── llm_setup.py         # Claude API configuration
├── tools/
│   ├── __init__.py
│   └── shell.py         # Shell tool với guardrails
├── test-api.sh          # Automated test suite (10 tests)
├── pyproject.toml       # uv dependencies
├── .env                 # API keys (không commit)
├── .env.example         # Template
├── README.md            # User-facing documentation
├── SUMMARY.md           # Implementation summary
└── TESTING.md           # Test documentation
```

## Key Patterns

### Adding New Tools

1. Tạo tool function trong `tools/` hoặc `agent.py`:

```python
def your_tool(arg: str) -> str:
    """Tool description for LLM"""
    # Validate input
    # Execute logic
    return result
```

2. Import và bind tool trong `agent.py`:

```python
from tools import run_shell_tool, your_tool

llm_with_tools = get_llm_with_tools([run_shell_tool, your_tool])
```

3. Handle tool execution trong `tool_node()`:

```python
if tool_call["name"] == "your_tool":
    result = your_tool(**tool_call["args"])
```

### Modifying Agent Loop

**Thêm node mới:**

```python
def your_node(state: AgentState) -> dict:
    """Node logic"""
    # Process state
    return {"status": "running"}  # Return state updates

workflow.add_node("your_node", your_node)
workflow.add_edge("some_node", "your_node")
```

**Thêm conditional routing:**

```python
def route_from_your_node(state: AgentState) -> Literal["option_a", "option_b"]:
    if condition:
        return "option_a"
    return "option_b"

workflow.add_conditional_edges(
    "your_node",
    route_from_your_node,
    {"option_a": "node_a", "option_b": "node_b"}
)
```

### Extending AgentState

Khi thêm field mới vào state:

1. Update `AgentState` TypedDict trong `agent.py`
2. Quyết định reducer: `add` (append) hay overwrite (default)
3. Update `initial_state` trong `api.py` và `agent.py`
4. Update nodes để set/read field mới

**Example:**

```python
class AgentState(TypedDict):
    # Existing fields...
    your_field: Annotated[list, add]  # Sử dụng add reducer để append
```

### Streaming Pattern

FastAPI SSE streaming với LangGraph:

```python
async def event_generator():
    for chunk in graph.stream(initial_state, stream_mode="updates"):
        for node_name, node_update in chunk.items():
            # Extract data từ node_update
            yield f"data: {json.dumps(data)}\n\n"

return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Stream modes:**
- `"updates"` - Nhận state updates từ mỗi node
- `"values"` - Nhận full state sau mỗi node
- `"messages"` - Nhận message updates only

## Configuration

### Environment Variables

Tạo `.env` file:

```bash
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_API_URL=https://api.anthropic.com
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Required:**
- `ANTHROPIC_API_KEY` - Claude API key từ console.anthropic.com

**Optional:**
- `ANTHROPIC_API_URL` - Default: https://api.anthropic.com
- `ANTHROPIC_MODEL` - Default: claude-3-5-sonnet-20241022

### Agent Configuration

Constants trong `agent.py`:

```python
MAX_ITERATIONS = 10  # Budget stop limit
```

Tool whitelist trong `tools/shell.py`:

```python
ALLOWED_PREFIXES = ("ls", "cat", "grep", "wc", "head", "find", "pwd")
EXCLUDE_PATTERNS = [".venv", "__pycache__", ".git", "node_modules", ".pyc"]
```

## Implementation Notes

### Why This Architecture?

**Planner node** giải quyết vấn đề:
- Model cần roadmap trước khi execute
- Replan khi verify fail thay vì retry mù quáng
- Separation of concerns: planning vs execution

**Verifier node** giải quyết vấn đề:
- Detect task completion thay vì dựa vào model self-assessment
- Catch errors và trigger replan
- Enforce quality gates trước khi kết thúc

**State management với TypedDict + reducers:**
- Type safety cho state schema
- `add_messages` reducer tự động handle message history
- Explicit về field nào append vs overwrite

### Known Limitations

1. **Shell tool whitelist**: Chỉ read-only commands, không có write/network operations
2. **No checkpointing**: Agent không lưu state giữa requests (stateless API)
3. **Single-turn conversation**: Mỗi request là independent task
4. **No human approval**: Agent execute tools automatically (no human-in-the-loop)
5. **Simple verifier**: Chỉ check response length và error keywords, không có semantic validation

### Future Extensions (Roadmap)

Các tính năng chưa implement nhưng architecture đã support:

- **Human approval node**: Thêm `"needs_approval"` status và approval endpoint
- **Checkpointing**: Pass `MemorySaver()` vào `create_agent_graph(checkpointer=...)`
- **Multi-turn conversation**: Thêm `conversation_id` và load history từ checkpoint
- **Advanced verifier**: Dùng LLM để verify output quality
- **More tools**: Database queries, web search, file write operations

## Testing Strategy

### Test Coverage

**test-api.sh** bao gồm:

1. Simple tasks (ls, pwd) - 2 iterations
2. Multi-step tasks (find + count) - 3+ iterations
3. File operations (cat, grep)
4. Error handling (disallowed commands)
5. Stream mode (SSE)
6. Edge cases (empty task)

### Manual Testing Workflow

1. Start server: `uv run python main.py`
2. Quan sát server logs để thấy:
   - Planning output
   - Request/Response JSON (với jq colors nếu có)
   - Tool executions
   - Verifier decisions
3. Test với curl hoặc test-api.sh
4. Check response format và correctness

### Debugging Tips

**Enable verbose logging:**
- Agent logs tự động in ra với jq formatting
- Mỗi LLM call hiển thị full request/response
- Tool results hiển thị colored JSON

**Common issues:**

1. **"ANTHROPIC_API_KEY not found"** → Check `.env` file exists và có key
2. **Tool timeout** → Command chạy quá 10s, simplify task hoặc tăng timeout
3. **Max iterations reached** → Task quá phức tạp, cần break down nhỏ hơn
4. **Stream không hoạt động** → Dùng `curl -N` flag để không buffer output

## Comparison với Lesson 2

Key differences từ minimal agent loop (lesson 2):

| Feature | Lesson 2 | Lesson 3 |
|---------|----------|----------|
| Loop control | Manual while loop | LangGraph StateGraph |
| State | List of dicts | TypedDict với reducers |
| Planning | Không có | Dedicated planner node |
| Verification | Không có | Dedicated verifier node |
| API | Không có | FastAPI REST + SSE |
| Streaming | Không có | Server-Sent Events |
| Replan | Không có | Auto-replan on error |

Lesson 3 production-ready hơn với explicit state machine, better error handling, và API layer cho integration.
