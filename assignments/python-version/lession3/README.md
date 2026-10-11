# LangGraph Agent API with FastAPI

FastAPI server với LangGraph agent integration - kết hợp pattern từ lession2.

## Tính năng

- ✅ **LangGraph State Machine**: Agent loop với state management
- ✅ **PostgreSQL Checkpointing**: Persistent conversation state
- ✅ **Human-in-the-Loop**: Approval workflow cho database queries
- ✅ **Tool Execution**: Shell command execution với guardrails
- ✅ **FastAPI Integration**: REST API endpoints
- ✅ **Streaming Support**: Server-Sent Events (SSE) cho real-time updates
- ✅ **Health Checks**: Monitoring endpoints

## Kiến trúc

```
┌─────────────┐
│   FastAPI   │ ← HTTP Request
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LangGraph  │ ← State Machine + Checkpointing
│    Agent    │
└──────┬──────┘
       │
       ├────────────────┐
       ▼                ▼
┌─────────────┐  ┌─────────────┐
│   Claude    │  │ PostgreSQL  │
│     API     │  │ Checkpoint  │
└─────────────┘  └─────────────┘
```

## Cài đặt

1. Clone repository
2. Cài đặt dependencies:
   ```bash
   uv sync
   ```

3. Tạo file `.env`:
   ```bash
   cp .env.example .env
   ```

4. Cập nhật `.env` với API key và database config:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key
   ANTHROPIC_API_URL=https://api.anthropic.com
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   
   # Database configuration
   DB_HOST=localhost
   DB_PORT=5433
   DB_NAME=agentdb
   DB_USER=agent
   DB_PASSWORD=agent123
   ```

5. Start PostgreSQL database:
   ```bash
   # Database đã chạy sẵn trong container
   docker ps | grep postgres
   
   # Hoặc start nếu chưa có
   docker start lession3-postgres
   ```

6. Setup checkpoint tables:
   ```bash
   uv run python db_setup.py
   ```

## Sử dụng

### Option 1: FastAPI Server

```bash
# Start server
uv run python main.py
```

Server chạy tại `http://localhost:8000`

Test API:
```bash
# Health check
curl http://localhost:8000/health

# Simple request
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List Python files", "thread_id": "demo-1"}'

# Database query (requires approval)
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List all tables in database", "thread_id": "demo-2"}'

# Approve the request
curl -X POST http://localhost:8000/agent/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "demo-2", "approved": true}'
```

### Option 2: Direct Client (giống lession2)

```bash
# Chạy agent trực tiếp với jq formatting
uv run python client.py
```

Client sẽ chạy 3 tasks demo và hiển thị kết quả với jq.

### Option 3: Standalone Agent

```bash
# Chạy agent.py trực tiếp (có thể import vào code khác)
uv run python -c "from agent import run_agent; print(run_agent('List files'))"
```

### Utilities

```bash
# Validation
uv run python validate.py

# Test suite
uv run python test-agent.py
```

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Run Agent (blocking)
```bash
# Simple request
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List all Python files in this directory", "thread_id": "user-123"}'

# Multi-turn conversation (remembers context)
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "How many files did we find?", "thread_id": "user-123"}'
```

#### Human Approval Workflow
```bash
# 1. Request database query (will pause for approval)
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List all database tables", "thread_id": "admin-1"}'

# Response: {"needs_approval": true, "approval_message": "Approve database query: list_tables({})?", ...}

# 2. Admin approves (returns result immediately)
curl -X POST http://localhost:8000/agent/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "admin-1", "approved": true}'

# Response: {"status": "completed", "result": "Here are all 7 tables...", ...}

# 3. Or reject with reason
curl -X POST http://localhost:8000/agent/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "admin-1", "approved": false, "reason": "Not authorized"}'
```

#### Stream Agent (SSE)
```bash
curl -N http://localhost:8000/agent/stream \
  -H "Content-Type: application/json" \
  -d '{"task": "List all Python files in this directory"}'
```

## Agent Components

### 1. State Management (LangGraph + PostgreSQL)

```python
class AgentState(TypedDict):
    task: str
    messages: Annotated[list, add_messages]
    tool_results: Annotated[list[dict], add]
    plan: str | None
    iteration: int
    status: Literal["running", "success", "failed", "needs_approval", "approved", "rejected"]
    verification_passed: bool
    error_message: str | None
    retry_count: int
    pending_tool_call: dict | None
    approval_message: str | None
```

**Checkpointing**: State được persist vào PostgreSQL sau mỗi node execution, cho phép:
- Resume conversation từ bất kỳ checkpoint nào
- Multi-turn conversations với context preservation
- Human-in-the-loop workflows với interrupt/resume

### 2. Agent Loop

```
START → planner → agent → approval_check → tools → verifier
           ↑                                          ↓
           └──────────────────────────────────────────┘
                    (replan if error)
```

**Human Approval Flow**:
```
agent → approval_check (interrupt if DB query) → wait for admin
                ↓ (approved)
              tools → continue execution
```

### 3. Termination Conditions

- **Natural stop**: Model không gọi thêm tool và verifier pass
- **Budget stop**: Đạt max iterations (configurable)
- **Error stop**: Critical error hoặc max retries exhausted
- **Human rejection**: Admin rejects approval request

### 4. Guardrails & Safety

**Tool Restrictions**:
- Shell commands: Only read-only (`ls`, `cat`, `grep`, `wc`, `head`, `find`, `pwd`)
- Database queries: **Require human approval** before execution
- Timeout: 10 seconds per tool execution
- Output limit: 4000 characters
- Retry logic: Exponential backoff (3 attempts max)

**Human-in-the-Loop**:
- Database queries (`query_db`, `list_tables`) automatically pause for approval
- Admin can approve or reject with custom reason
- Approved requests execute and return results immediately
- Rejected requests fail with admin's rejection message

### 5. PostgreSQL Checkpointing

**Database Tables** (auto-created):
- `checkpoints`: Main state snapshots with JSONB data
- `checkpoint_writes`: Intermediate writes within checkpoints
- `checkpoint_blobs`: Binary data (messages, tool results)
- `checkpoint_migrations`: Schema version tracking

**Benefits**:
- Conversation continuity across requests
- Resume from any point after server restart
- Audit trail of all agent executions
- Multi-session isolation by thread_id

## So sánh với Lession2

| Feature | Lession2 (Minimal) | Lession3 (LangGraph + FastAPI) |
|---------|-------------------|--------------------------------|
| Agent Loop | Manual while loop | LangGraph state machine |
| State Management | List of dicts | TypedDict với StateGraph |
| Persistence | None | PostgreSQL checkpointing |
| Tool Execution | Direct function call | Tool binding với LangChain |
| Human Approval | None | Interrupt-based approval workflow |
| API | None | FastAPI với REST + SSE |
| Streaming | None | Server-Sent Events |
| Multi-turn | None | Thread-based conversation memory |
| Error Handling | Basic try-catch | Retry logic + exponential backoff |

## Cấu trúc Project

```
lession3/
├── main.py                # Entry point (start FastAPI server)
├── api.py                 # FastAPI layer (HTTP endpoints)
├── agent.py               # LangGraph core (state machine + tools)
├── db_setup.py            # PostgreSQL checkpointer setup
├── llm_setup.py           # LLM configuration
├── tools.py               # Tool definitions (shell, database)
├── client.py              # Agent client với jq formatting
├── test-agent.py          # Test suite
├── test-checkpointing.sh  # Checkpointing test script
├── test-approval.sh       # Human approval test script
├── validate.py            # Validation script
├── pyproject.toml         # Dependencies
├── .env.example           # Environment template
├── README.md              # Documentation
├── CHECKPOINTING.md       # Checkpointing implementation guide
└── docs/                  # Additional documentation
```

### Agent Flow

**LangGraph State Machine:**

```mermaid
graph TD
    START([START]) --> planner[Planner Node]
    planner --> agent[Agent Node]
    agent --> should_continue{should_continue?}
    
    should_continue -->|has tool_calls| tools[Tool Node]
    should_continue -->|no tool_calls| verifier[Verifier Node]
    
    tools --> agent
    
    verifier --> route{route_after_verify?}
    
    route -->|max iterations| END([END])
    route -->|verification passed| END
    route -->|failed/error| planner
    route -->|continue| agent
    
    style START fill:#e1f5e1
    style END fill:#ffe1e1
    style planner fill:#e3f2fd
    style agent fill:#fff3e0
    style tools fill:#f3e5f5
    style verifier fill:#e8f5e9
    style should_continue fill:#fff9c4
    style route fill:#fff9c4
```

**Nodes:**
- `planner_node`: Tạo plan hoặc replan khi có error
- `agent_node`: Gọi LLM với tools dựa trên plan
- `approval_check_node`: Check if tools need human approval (uses `interrupt()`)
- `tool_node`: Execute tools (shell, database) với validation và retry
- `verifier_node`: Kiểm tra task completion và detect errors

**Routing Logic:**
- `should_continue`: agent → approval_check (nếu có tool_calls) hoặc verifier
- `approval_check`: Interrupt graph nếu database query, otherwise continue
- `route_after_verify`: verifier → planner (replan) | agent (continue) | END

**Termination Conditions:**
- Natural stop: Model không gọi thêm tool và verifier pass
- Budget stop: Đạt MAX_ITERATIONS
- Error stop: Verifier detect error và trigger replan
- Human rejection: Admin rejects approval request

**Tools:**
- `run_shell_tool`: Shell commands (ls, cat, grep, wc, head, find, pwd) - **No approval**
- `query_db`: Execute SQL queries - **Requires approval**
- `list_tables`: List database tables - **Requires approval**

**Integration Flow:**

```
Cách 1: Qua API
  main.py (uvicorn) → api.py (FastAPI) → agent.py (LangGraph)

Cách 2: Direct client
  client.py → agent.py (LangGraph)
```

## Dependencies

- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `langgraph`: State machine cho agents
- `langgraph-checkpoint-postgres`: PostgreSQL checkpointing
- `langchain-anthropic`: Claude integration
- `python-dotenv`: Environment variables
- `psycopg`: PostgreSQL driver

## Advanced Usage

### Custom Tools

Thêm tools mới trong `tools.py`:

```python
def your_custom_tool(arg: str) -> str:
    """Your tool description"""
    # Implementation
    return result
```

Bind to agent trong `agent.py`:
```python
tools = [run_shell_tool, query_db, list_tables, your_custom_tool]
llm_with_tools = get_llm_with_tools(tools)
```

### Checkpointing (Conversation Memory)

**Automatic checkpointing** - mỗi conversation được lưu vào PostgreSQL:

```python
from db_setup import get_checkpointer
from agent import create_agent_graph

checkpointer = get_checkpointer()
graph = create_agent_graph(checkpointer=checkpointer)

# Each thread_id is an isolated conversation
config = {"configurable": {"thread_id": "user-123"}}
result = graph.invoke(initial_state, config=config)
```

**Resume conversation**:
```bash
# First request
curl POST /agent/run {"task": "List files", "thread_id": "user-123"}

# Second request - remembers first request
curl POST /agent/run {"task": "How many files?", "thread_id": "user-123"}
```

**Inspect checkpoints**:
```bash
# View all checkpoints for a thread
PGPASSWORD=agent123 psql -h localhost -p 5433 -U agent -d agentdb -c \
  "SELECT checkpoint_id, parent_checkpoint_id FROM checkpoints WHERE thread_id = 'user-123';"
```

### Human-in-the-Loop Approval

**Add approval for custom tools** in `agent.py`:

```python
def approval_check_node(state: AgentState) -> dict:
    for tool_call in last_message.tool_calls:
        tool_name = tool_call['name']
        
        # Add your tool to approval list
        if tool_name in ['query_db', 'list_tables', 'your_sensitive_tool']:
            approval = interrupt({
                "type": "approval_required",
                "tool": tool_name,
                "args": tool_call.get('args', {}),
                "message": f"Approve {tool_name}?",
            })
            
            if not approval.get("approved"):
                return {"status": "failed", "error_message": "Rejected"}
    
    return {"status": "running"}
```

**Workflow**:
1. User request triggers sensitive tool → Graph pauses với `interrupt()`
2. API returns `needs_approval: true`
3. Admin calls `/agent/approve` với `approved: true/false`
4. Graph resumes với `Command(resume={approved: ...})`
5. Tool executes (if approved) hoặc fails (if rejected)

## Troubleshooting

### Import errors
```bash
# Đảm bảo đang dùng virtual environment
uv sync
source .venv/bin/activate  # hoặc .venv\Scripts\activate trên Windows
```

### API key not found
```bash
# Kiểm tra .env file
cat .env
# Đảm bảo không có khoảng trắng: ANTHROPIC_API_KEY=sk-...
```

### Database connection errors
```bash
# Check PostgreSQL running
docker ps | grep postgres

# Start container if stopped
docker start lession3-postgres

# Verify connection
PGPASSWORD=agent123 psql -h localhost -p 5433 -U agent -d agentdb -c "\dt"

# Re-run setup if tables missing
uv run python db_setup.py
```

### Port already in use
```bash
# Thay đổi port trong main.py
uvicorn.run("api:app", host="0.0.0.0", port=8001)
```

### Approval not working
```bash
# Check if interrupt is detected in logs
# Look for: "⚠ Tool 'list_tables' requires human approval"

# Verify thread state
uv run python -c "
from agent import create_agent_graph
from db_setup import get_checkpointer
graph = create_agent_graph(get_checkpointer())
state = graph.get_state({'configurable': {'thread_id': 'YOUR_THREAD_ID'}})
print(f'Next: {state.next}')
print(f'Has interrupts: {any(hasattr(t, \"interrupts\") for t in state.tasks)}')
"
```

## Testing

### Run Test Suites
```bash
# Basic agent tests
uv run python test-agent.py

# Checkpointing tests
./test-checkpointing.sh

# Human approval tests
./test-approval.sh
```

### Manual Testing
```bash
# Start server in one terminal
uv run python main.py

# Test in another terminal
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List tables", "thread_id": "test-1"}' | jq

# If needs_approval: true
curl -X POST http://localhost:8000/agent/approve \
  -H "Content-Type: application/json" \
  -d '{"thread_id": "test-1", "approved": true}' | jq
```

## Tham khảo

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [PostgreSQL Checkpointer](https://langchain-ai.github.io/langgraph/reference/checkpoints/#langgraph.checkpoint.postgres.PostgresSaver)
- [Session 2 Materials](../lession2/)

## Key Features Summary

✅ **Multi-turn Conversations**: Thread-based memory với PostgreSQL checkpointing
✅ **Human Approval**: Database queries pause for admin approval
✅ **Error Recovery**: Retry logic với exponential backoff + replan capability
✅ **Safety Guardrails**: Read-only shell commands, approval workflow
✅ **Real-time Streaming**: SSE support for live updates
✅ **Audit Trail**: Full checkpoint history in database
✅ **Session Isolation**: Independent conversations per thread_id

## API Endpoints Reference

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/` | GET | Root endpoint | No |
| `/health` | GET | Health check | No |
| `/agent/run` | POST | Execute agent task | No |
| `/agent/stream` | POST | Stream agent execution (SSE) | No |
| `/agent/approve` | POST | Approve/reject pending action | Admin |

## Example Workflows

### 1. Simple Query
```bash
curl POST /agent/run {"task": "List Python files", "thread_id": "user-1"}
# → Executes immediately, returns result
```

### 2. Database Query with Approval
```bash
# User request
curl POST /agent/run {"task": "List tables", "thread_id": "user-2"}
# → {"needs_approval": true, ...}

# Admin approves
curl POST /agent/approve {"thread_id": "user-2", "approved": true}
# → {"status": "completed", "result": "...7 tables..."}
```

### 3. Multi-turn Conversation
```bash
# First request
curl POST /agent/run {"task": "List files", "thread_id": "user-3"}
# → "Found 5 files: api.py, agent.py, ..."

# Second request (remembers context)
curl POST /agent/run {"task": "How many?", "thread_id": "user-3"}
# → "We found 5 files"
```
