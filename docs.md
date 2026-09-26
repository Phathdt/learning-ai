# Masterclass Agent Engineering & AgentOps

## Detailed Curriculum --- 20 buổi × 2 giờ

> **Learning path:** Understand → Build → Context → Knowledge → Tools →
> Coordinate → Evaluate → Secure → Serve → Deliver → Prepare →
> Containerize → Deploy → Automate → Observe → Evaluate Continuously →
> Optimize → Run Durably → Operate

---

# Phần I --- Masterclass Agent Engineering

## Buổi 1 --- Modern Agent Systems and Harness

### Mục tiêu

Sau buổi học, học viên có thể: - Phân biệt LLM application, workflow và
autonomous/semi-autonomous agent. - Hiểu agent không chỉ là prompt + LLM
mà là **Model + Harness + Environment**. - Đọc được execution trace của
một agent. - Hiểu vì sao Claude Code, ChatGPT, Cursor cần một agent
harness thay vì một prompt đơn giản.

### Theory --- 50--60 phút

#### 1. Từ LLM application đến Agent

- LLM inference cơ bản.
- Chat completion và structured output.
- Function/tool calling.
- Workflow cố định:
  - Sequential workflow.
  - Router.
  - Parallel execution.
  - Evaluator-optimizer.
- Agent:
  - Model tự quyết định bước tiếp theo.
  - Quan sát state/environment.
  - Chọn tool.
  - Kiểm tra kết quả.
  - Lặp cho đến khi đạt termination condition.
- Khi nào **không nên dùng agent**.

#### 2. Agent = Model + Harness

Phân tích các thành phần: - Model. - System prompt/instructions. -
Context builder. - Conversation/session state. - Tools. - Tool result
handling. - Memory. - Skills/instructions. - Retrieval. - Execution
environment. - Guardrails. - Human approval. - Persistence/checkpoint. -
Observability. - Evaluation.

#### 3. Anatomy của một Agent Loop

```text
User Request
    ↓
Build Context
    ↓
Model
    ↓
Decision
 ┌──┴─────────────┐
 │                │
Answer          Tool Call
 │                ↓
 │             Execute
 │                ↓
 │             Observe
 │                ↓
 └───────→ Model
              ↓
           Verify
              ↓
            Final
```

- Observe → Think/Decide → Act → Verify.
- Tool call có thể làm thay đổi state.
- Context được cập nhật sau mỗi action.
- Termination condition.

#### 4. Execution environment

- Filesystem.
- Database.
- APIs.
- Browser.
- Sandbox.
- External services.
- Trust boundary giữa agent và environment.

#### 5. Case study

Phân tích conceptually: - Claude Code. - ChatGPT agentic workflows. -
Cursor. - Coding agent vs research agent vs operations agent.

### Lab --- 60--70 phút

**Explore một agent harness có sẵn.**

Học viên: 1. Gửi một task. 2. Quan sát model invocation. 3. Quan sát
tool discovery. 4. Quan sát tool call. 5. Quan sát tool result. 6. Quan
sát context thay đổi. 7. Quan sát termination. 8. Xác định những thành
phần nào thuộc harness.

### Output

- Agent architecture diagram.
- Execution trace annotated.
- Danh sách các building block cần xây trong 19 buổi tiếp theo.

---

## Buổi 2 --- Agent Loop Engineering with LangGraph

### Mục tiêu

- Tự xây agent loop có state.
- Hiểu LangGraph ở mức architecture, không chỉ API.
- Có persistence, checkpoint, retry, resume và human approval.

### Theory

#### 1. LangGraph mental model

- State.
- Node.
- Edge.
- Conditional edge.
- Graph execution.
- Checkpoint.
- Interrupt/resume.
- Reducer/state update.

#### 2. Thiết kế Agent State

Ví dụ:

```python
class AgentState(TypedDict):
    messages: list
    task: str
    tool_results: list
    iteration: int
    status: str
```

Phân biệt: - Ephemeral state. - Session state. - Persistent state.

#### 3. Agent Loop

- Observe.
- Decide.
- Act.
- Verify.
- Continue/stop.

#### 4. Failure modes

- Infinite loop.
- Premature termination.
- Repeated tool call.
- Invalid tool arguments.
- Tool timeout.
- Model refusal.
- Partial failure.

#### 5. Reliability patterns

- Max iterations.
- Timeout.
- Retry.
- Exponential backoff.
- Idempotency.
- Checkpoint.
- Resume.
- Human approval.
- Fallback.

#### 6. Streaming

- Token streaming.
- Event streaming.
- Node progress.
- Tool activity.
- Final response.

### Lab

Xây:

```text
User
 ↓
Planner/Agent
 ↓
Tool
 ↓
Verifier
 ↓
Agent
 ↓
Final Answer
```

Bổ sung: - Persistent checkpoint. - Streaming events. - Max iteration. -
Retry. - Human approval trước destructive action. - Resume từ
checkpoint.

### Output

Một agent loop có stateful execution và có thể resume sau interruption.

---

## Buổi 3 --- Tool and MCP Engineering

### Mục tiêu

- Thiết kế tool contract tốt.
- Hiểu MCP architecture.
- Xây remote MCP server có authentication và least privilege.

### Theory

#### 1. Tool calling

- Tool schema.
- Input validation.
- Structured output.
- Tool descriptions.
- Tool naming.
- Error semantics.

#### 2. Tool design principles

Tool tốt cần: - Narrow responsibility. - Deterministic contract. -
Explicit permission boundary. - Predictable error. - Idempotency nếu có
side effect. - Observable execution. - Testable independently.

#### 3. Tool categories

- Database.
- SQL.
- REST API.
- Search.
- RAG.
- Filesystem.
- Sandbox.
- Business operation.

#### 4. MCP

- Host.
- Client.
- Server.
- Tools.
- Resources.
- Prompts/capabilities.
- Discovery.
- Transport.
- Authentication.

#### 5. Security

- Least privilege.
- Authentication vs authorization.
- Credential isolation.
- Tool allowlist.
- Audit trail.
- Rate limit.
- Retry policy.

### Lab

Xây:

```text
Agent
  ↓
MCP Client
  ↓
Remote MCP Server
  ↓
Read-only Database
```

Thực hiện: - Schema discovery. - Read-only SQL tool. - Input
validation. - Authentication. - Authorization. - Audit logging. - Error
handling. - Connect từ MCP-compatible host.

### Output

Remote read-only MCP server + security boundary + tool tests.

---

## Buổi 4 --- Context Engineering with Prompts, Skills and Memory

### Mục tiêu

- Hiểu context window như một tài nguyên hữu hạn.
- Thiết kế context pipeline.
- Phân biệt prompt, skill, session state và memory.
- Isolate context giữa users.

### Theory

#### 1. Anatomy của Agent Context

```text
System Instructions
+ User Request
+ Conversation
+ Skills
+ Retrieved Knowledge
+ Tool Results
+ Memory
+ Runtime State
```

#### 2. Context engineering

- Context selection.
- Context ordering.
- Context compression.
- Summarization.
- Deduplication.
- Relevance filtering.
- Token budgeting.

#### 3. Prompt engineering cho agent

- Role/instruction.
- Tool-use instruction.
- Decision policy.
- Verification instruction.
- Output contract.
- Failure behavior.

#### 4. Skills

- Skill là instruction/module có thể tái sử dụng.
- Skill discovery.
- Skill activation.
- Skill composition.
- Skill precedence.
- Skill versioning.

#### 5. Memory

- Short-term memory.
- Long-term memory.
- Semantic memory.
- Episodic memory.
- User preference.
- Task memory.
- Memory write policy.
- Memory retrieval policy.
- Memory deletion/correction.

#### 6. Filesystem và artifacts

- Workspace.
- Intermediate artifacts.
- Durable files.
- User isolation.

### Lab

Xây:

```text
Request
 ↓
Context Builder
 ├── System Prompt
 ├── Skill
 ├── Session Memory
 ├── Long-term Memory
 └── Runtime State
 ↓
Agent
```

Bổ sung: - Token budget. - User namespace. - Memory read/write policy. -
Context filtering.

### Output

Context pipeline + một Skill + memory system multi-user.

---

## Buổi 5 --- Advanced Retrieval and Vector Databases

### Mục tiêu

- Hiểu RAG như một tool trong agent loop.
- Xây retrieval pipeline với Qdrant.
- Đánh giá retrieval quality.
- Trả lời có source citation.

### Theory

#### 1. RAG architecture

```text
Documents
 ↓
Chunking
 ↓
Embedding
 ↓
Vector DB
 ↓
Query
 ↓
Retrieval
 ↓
Filtering/Reranking
 ↓
Context
 ↓
LLM
```

#### 2. Embeddings

- Semantic representation.
- Embedding model.
- Dimension.
- Similarity.
- Cosine similarity.

#### 3. Chunking

- Fixed-size.
- Recursive.
- Semantic.
- Structure-aware.
- Chunk overlap.
- Metadata.

#### 4. Qdrant

- Collection.
- Vector.
- Payload.
- Index.
- Filter.
- Similarity search.

#### 5. Retrieval quality

- Precision.
- Recall.
- Top-k.
- Relevance.
- Source coverage.
- Freshness.
- Missing knowledge.

#### 6. Advanced retrieval

- Metadata filtering.
- Hybrid retrieval.
- Query expansion.
- Multi-query.
- Reranking.
- Context compression.

#### 7. Multi-tenant retrieval

- Tenant ID.
- Authorization filter.
- Namespace.
- Prevent cross-tenant leakage.

### Lab

Xây Qdrant retrieval tool: - Ingest knowledge base. - Generate
embeddings. - Store metadata. - Query. - Apply tenant filter. - Return
source metadata. - Integrate into agent loop. - Generate citations.

### Output

RAG tool có filtering, source metadata và citation.

---

## Buổi 6 --- Multi-Agent Engineering

### Mục tiêu

- Biết khi nào một agent là đủ.
- Thiết kế multi-agent workflow.
- Quản lý delegation, parallelism và failure.

### Theory

#### 1. Single agent vs multi-agent

Không dùng multi-agent chỉ vì có thể.

So sánh: - Agent + Skills. - Agent + Tools. - Subagent. - Specialist
agents.

#### 2. Patterns

- Supervisor.
- Router.
- Handoff.
- Subagent-as-tool.
- Pipeline.
- Parallel specialists.
- Debate/critic.

#### 3. Delegation contract

Task cần truyền: - Objective. - Context. - Constraints. - Expected
output. - Evidence requirement. - Timeout.

#### 4. Parallel execution

- Fan-out.
- Fan-in.
- Async execution.
- Timeout.
- Partial failure.
- Cancellation.

#### 5. Conflict resolution

- Evidence-based merge.
- Confidence.
- Source priority.
- Critic/verifier.

#### 6. Cost control

- Model selection.
- Token budget.
- Max subagents.
- Parallelism limits.
- Early termination.

### Lab

Xây hai workflow:

**Executor--Advisor**

```text
Supervisor
 ├── Executor
 └── Advisor
        ↓
     Supervisor
```

**Research Team**

```text
Researcher A ─┐
Researcher B ─┼→ Synthesizer → Verifier
Researcher C ─┘
```

### Output

Multi-agent workflow có parallel execution, timeout và conflict
handling.

---

## Buổi 7 --- Observability and Evaluation Engineering

### Mục tiêu

- Hiểu vì sao agent evaluation khác traditional API testing.
- Trace toàn bộ agent trajectory.
- Xây eval dataset và regression suite.

### Theory

#### 1. Agent observability

Cần quan sát: - User request. - Model. - Prompt. - Context. - Tool
calls. - Retrieval. - Tool latency. - Token usage. - Cost. - Final
output. - Errors.

#### 2. Evaluation dimensions

- Final answer quality.
- Task success.
- Tool selection.
- Tool arguments.
- Retrieval relevance.
- Groundedness.
- Safety.
- Latency.
- Cost.

#### 3. Evaluation levels

- Unit evaluation.
- Component evaluation.
- Trajectory evaluation.
- End-to-end evaluation.
- Production evaluation.

#### 4. Evaluator types

- Exact/code evaluator.
- Rule-based evaluator.
- LLM-as-a-judge.
- Human review.

#### 5. Dataset

- Golden cases.
- Edge cases.
- Failure cases.
- Regression cases.
- Adversarial cases.

### Lab

Với Langfuse: - Instrument agent. - Build dataset. - Run experiments. -
Compare baseline/candidate. - Create regression cases. - Inspect failed
traces.

### Output

Eval dataset + experiment report + regression suite.

---

## Buổi 8 --- Security, Guardrails and Governance

### Mục tiêu

- Threat-model một agent.
- Nhận diện prompt injection và data leakage.
- Implement defense-in-depth.

### Theory

#### 1. Threat model

Assets: - User data. - Credentials. - Tools. - Knowledge base. -
Filesystem. - External APIs.

Attack surface: - User prompt. - Retrieved content. - Tool output. -
Files. - MCP server. - Third-party API.

#### 2. Prompt injection

- Direct injection.
- Indirect injection.
- Retrieved-document injection.
- Tool-output injection.

#### 3. Data leakage

- Cross-user memory.
- Cross-tenant retrieval.
- Sensitive tool result.
- Prompt/context leakage.
- Logs containing secrets/PII.

#### 4. Authentication and authorization

- Identity.
- Session.
- Tenant.
- RBAC/ABAC.
- Tool permissions.

#### 5. Guardrails

- Input guardrail.
- Context guardrail.
- Tool guardrail.
- Output guardrail.
- Human approval.

#### 6. Sandbox

- Filesystem.
- Network.
- Process.
- Resource limits.

#### 7. Audit

- Who.
- What.
- When.
- Which tool.
- Which resource.
- Result.

### Lab

**Attack & Defend** - Prompt injection. - Malicious retrieved
document. - Unauthorized tool. - Cross-user access. - Secret leakage.

Sau đó bổ sung: - Guardrails. - Authorization. - Tool policy. - Human
approval. - Security regression tests.

### Output

Threat model + security controls + attack/defense test suite.

---

## Buổi 9 --- Agent API Engineering with FastAPI

### Mục tiêu

- Expose agent thành production-oriented API.
- Hiểu session và streaming.
- Thiết kế API multi-user.

### Theory

#### 1. API architecture

```text
Client
 ↓
FastAPI
 ↓
Session/Auth
 ↓
Agent Runtime
 ↓
Tools / Retrieval / MCP
```

#### 2. API contract

- Request schema.
- Response schema.
- Error schema.
- Validation.
- Versioning.

#### 3. SSE

- Event stream.
- Connection lifecycle.
- Event types.
- Tool activity.
- Agent progress.
- Final result.

Ví dụ:

```text
agent.started
agent.thinking
tool.started
tool.completed
agent.progress
agent.completed
agent.failed
```

#### 4. Session

- Session ID.
- User ID.
- Tenant ID.
- Conversation state.
- Authorization.

#### 5. Reliability

- Timeout.
- Cancellation.
- Error handling.
- Health endpoint.
- Readiness/liveness concept.

### Lab

Xây: - FastAPI service. - `/agent/run`. - `/agent/stream`. - SSE. -
Session management. - Authentication. - User isolation. - Health
check. - Structured logs.

### Output

Agent API + starter UI integration.

---

## Buổi 10 --- Build Your Production-Ready Agent

### Mục tiêu

Tổng hợp toàn bộ kiến thức thành một agent hoàn chỉnh.

### Theory

#### Architecture review

- Agent loop.
- Context.
- Memory.
- Retrieval.
- Tools/MCP.
- Multi-agent.
- Evaluation.
- Security.
- API.

#### Architecture decision

Học viên phải giải thích: - Vì sao chọn architecture này? - Vì sao dùng
agent? - Vì sao dùng tool này? - Vì sao cần memory? - Vì sao cần
multi-agent hoặc không? - Failure modes là gì? - Security boundary ở
đâu?

### Lab

Mỗi học viên/team: 1. Chọn use case. 2. Hoàn thiện agent. 3. Chạy eval. 4. Xử lý failure scenario. 5. Demonstrate security control. 6.
Demonstrate observability. 7. Present architecture.

### Deliverables

- Working agent.
- Architecture diagram.
- Evaluation results.
- Security checklist.
- Failure analysis.
- Improvement backlog.

---

# Phần II --- Masterclass AgentOps

## Buổi 11 --- AgentOps: From Prototype to Production

### Mục tiêu

- Hiểu AgentOps lifecycle.
- Chuẩn hóa project để reproducible.
- Version hóa mọi thành phần quan trọng.

### Theory

#### 1. Agent lifecycle

```text
Develop
 ↓
Test
 ↓
Evaluate
 ↓
Package
 ↓
Deploy
 ↓
Observe
 ↓
Evaluate
 ↓
Improve
 ↓
Release
```

#### 2. MLOps vs AgentOps

AgentOps có thêm: - Prompt versioning. - Tool versioning. - Retrieval
changes. - Model changes. - Agent trajectory. - Evaluation datasets. -
Guardrail policies. - Dynamic behavior.

#### 3. Project structure

Ví dụ:

```text
agent/
├── app/
├── agents/
├── tools/
├── retrieval/
├── memory/
├── evaluation/
├── tests/
├── prompts/
├── skills/
├── infra/
└── scripts/
```

#### 4. Dependency management

- Lockfile.
- Pinning.
- Reproducible environment.
- Python virtual environment.
- Dependency update policy.

#### 5. Configuration

- Development.
- Staging.
- Production.
- Environment variables.
- Secret references.

#### 6. Versioning

Version: - Code. - Prompt. - Model. - Tools. - Knowledge base. -
Evaluation dataset. - Agent configuration.

### Lab

- Chuẩn hóa repository.
- Environment config.
- Dependency lock.
- Baseline release.
- Git tagging.
- Reproducible run.

### Output

Agent repository có baseline release có thể tái lập.

---

## Buổi 12 --- Serving an Agent with FastAPI

### Mục tiêu

- Xây API phục vụ agent production.
- Streaming ổn định.
- Chuẩn hóa authentication/session/logging.

### Theory

- FastAPI application lifecycle.
- Dependency injection.
- Pydantic schemas.
- Async execution.
- SSE.
- Request cancellation.
- Session metadata.
- Authentication.
- Data isolation.
- Error handling.
- Health/readiness.
- Application logs.

### Lab

Nâng cấp starter agent: - `/v1/agent/run`. - `/v1/agent/stream`. - Auth
middleware. - Session metadata. - Structured logs. - Health/readiness. -
Error contract.

### Output

Agent API ready for containerization.

---

## Buổi 13 --- Containerizing Agents with Docker

### Mục tiêu

- Đóng gói agent reproducibly.
- Hiểu production Docker image.
- Chạy toàn bộ stack local.

### Theory

- Image vs container.
- Layers.
- Build cache.
- Multi-stage build.
- Dependency pinning.
- `.dockerignore`.
- Environment variables.
- Secrets.
- Networking.
- Volumes.
- Graceful shutdown.
- Health check.

### Dockerfile principles

- Minimal base image.
- Non-root user.
- Deterministic dependencies.
- Cache dependencies.
- No secrets in image.

### Lab

Dockerize:

```text
FastAPI Agent
Qdrant
Database
Supporting services
```

Dùng Docker Compose: - Networking. - Environment. - Health checks. -
Startup dependency. - Persistent volumes.

### Output

Dockerized local Agent stack.

---

## Buổi 14 --- Deploying an Agent to Cloud

### Mục tiêu

- Hiểu cloud runtime cho agent.
- Deploy lên Google Cloud Run.
- Quản lý secrets và identity.

### Theory

#### Cloud architecture

```text
Internet
 ↓
Cloud Run
 ↓
Agent API
 ├── LLM Provider
 ├── Qdrant
 ├── Database
 └── Langfuse
```

#### Topics

- Container registry.
- Cloud Run.
- Stateless runtime.
- Request timeout.
- Concurrency.
- Autoscaling.
- Cold start.
- Environment variables.
- Secret Manager.
- IAM.
- Service account.
- Logging.
- Rollback.
- Cost control.

### Lab

- Build image.
- Push Artifact Registry.
- Deploy Cloud Run.
- Configure service account.
- Configure Secret Manager.
- Configure environment.
- Test public URL.
- Deploy revision.
- Roll back revision.

### Output

Publicly accessible cloud Agent API.

---

## Buổi 15 --- CI/CD with GitHub Actions

### Mục tiêu

- Tự động hóa test → build → deploy.
- Thiết kế release workflow.
- Có rollback và environment separation.

### Theory

#### CI

- Lint.
- Unit test.
- Integration test.
- Agent behavior test.
- Security test.

#### CD

```text
Git Push
 ↓
CI
 ↓
Build
 ↓
Container
 ↓
Registry
 ↓
Deploy
 ↓
Smoke Test
 ↓
Release
```

#### GitHub Actions

- Workflow.
- Job.
- Step.
- Matrix.
- Secret.
- Environment.
- Artifact.
- Cache.

#### Release strategy

- Development.
- Staging.
- Production.
- Manual approval.
- Rollback.

### Lab

Build pipeline: 1. Test. 2. Build image. 3. Push registry. 4. Deploy
Cloud Run. 5. Smoke test. 6. Record release version.

### Output

One-command / automated deployment pipeline.

---

## Buổi 16 --- Observability for Agent Systems

### Mục tiêu

- Quan sát service và agent cùng một hệ thống.
- Correlate API request với agent trace.
- Điều tra một lỗi từ đầu đến cuối.

### Theory

#### Three pillars

- Logs.
- Metrics.
- Traces.

#### Structured logging

Ví dụ fields:

```json
{
  "request_id": "...",
  "user_id": "...",
  "session_id": "...",
  "agent_run_id": "...",
  "event": "tool.completed",
  "latency_ms": 1240
}
```

#### Distributed tracing

- Trace.
- Span.
- Parent/child.
- Trace ID.
- Correlation.

#### OpenTelemetry

- Instrumentation.
- Exporter.
- Collector.
- Semantic conventions.

#### Agent tracing

- Model call.
- Tool call.
- Retrieval.
- Agent node.
- Evaluation.

#### Metrics

- Request rate.
- Error rate.
- P95 latency.
- Token usage.
- Cost.
- Tool failure rate.
- Agent success rate.

### Lab

- Langfuse instrumentation.
- OpenTelemetry instrumentation.
- Grafana dashboard.
- Correlate request → service trace → agent trace.
- Investigate one failed request.

### Output

Observability dashboard + investigated incident trace.

---

## Buổi 17 --- Continuous Evaluation with Langfuse

### Mục tiêu

- Chuyển evaluation từ hoạt động thủ công thành production feedback
  loop.
- Chặn release làm giảm quality.

### Theory

#### AI Engineering Loop

```text
Deploy
 ↓
Collect Traces
 ↓
Identify Failure
 ↓
Add Dataset Case
 ↓
Evaluate
 ↓
Improve
 ↓
Compare
 ↓
Release
```

#### Offline evaluation

- Before release.
- Golden dataset.
- Regression suite.
- Baseline/candidate.

#### Online evaluation

- Production traces.
- Sampling.
- User feedback.
- Failure detection.

#### Quality gate

Ví dụ: - Task success \>= threshold. - Safety pass rate \>= threshold. -
Regression count \<= threshold.

### Lab

- Create regression dataset.
- Run baseline.
- Run candidate.
- Compare metrics.
- Add quality gate.
- Integrate result into CI/CD.

### Output

Continuous evaluation workflow + release quality gate.

---

## Buổi 18 --- Optimizing Cost and Latency

### Mục tiêu

- Tìm bottleneck bằng data.
- Tối ưu cost/latency nhưng không phá quality.
- Hiểu trade-off giữa model, context, tools và infrastructure.

### Theory

#### Cost model

```text
Total Cost =
Model Input
+ Model Output
+ Tool/API
+ Retrieval
+ Infrastructure
+ Observability
```

#### Latency model

```text
T_total =
Model latency
+ Tool latency
+ Retrieval latency
+ Network latency
+ Queue latency
+ Serialization
```

#### Optimization areas

**Model** - Smaller model. - Routing. - Batch. - Temperature/parameters.

**Context** - Compression. - Summarization. - Retrieval filtering. -
Remove redundant context.

**Tools** - Parallel calls. - Cache. - Reduce unnecessary calls. -
Better tool granularity.

**Infrastructure** - Connection pooling. - Concurrency. - Autoscaling. -
Caching.

#### AI Gateway

- Routing.
- Load balancing.
- Rate limiting.
- Usage tracking.
- Model fallback.

### Lab

1. Find bottleneck in Langfuse.
2. Establish baseline.
3. Apply one or more optimizations.
4. Measure:
   - Cost.
   - Latency.
   - Quality.
5. Compare before/after.

### Output

Optimization report with quantified trade-offs.

---

## Buổi 19 --- Durable Execution and High Throughput

### Mục tiêu

- Biết khi nào request-response không còn phù hợp.
- Xây background agent execution.
- Có retry, resume, idempotency và progress tracking.

### Theory

#### Synchronous agent

```text
Client
 ↓
HTTP Request
 ↓
Agent
 ↓
Response
```

Vấn đề: - Long-running. - Connection timeout. - User disconnect. -
Worker crash.

#### Durable architecture

```text
Client
 ↓
API
 ↓
Queue
 ↓
Worker
 ↓
Agent
 ↓
State/Checkpoint
```

#### Task lifecycle

```text
created
 → queued
 → running
 → completed
```

Failure:

```text
running
 → failed
 → retrying
 → running
```

#### Concepts

- Message queue.
- Worker.
- Task ID.
- State store.
- Checkpoint.
- Retry.
- Backoff.
- Dead-letter queue.
- Idempotency.
- Cancellation.
- Resume.
- Progress events.

#### High throughput

- Worker pool.
- Concurrency.
- Backpressure.
- Rate limiting.
- Queue depth.
- Per-user quotas.

### Lab

Nâng cấp Agent API: 1. `POST /tasks`. 2. Queue task. 3. Worker nhận
task. 4. Execute agent. 5. Persist state. 6. Track progress. 7. Query
status. 8. Kill worker. 9. Restart worker. 10. Resume task. 11. Test
duplicate delivery/idempotency.

### Output

Durable background Agent execution system.

---

## Buổi 20 --- Production Game Day and Final Project

### Mục tiêu

- Vận hành agent như production system.
- Điều tra incident bằng evidence.
- Rollback và phục hồi.
- Viết production runbook.

### Theory

#### Production readiness

Checklist: - API. - Authentication. - Authorization. - Secrets. -
Observability. - Evaluation. - Security. - Backup/state. - Scaling. -
Cost controls. - Alerts. - Rollback. - Runbook.

#### Incident response

```text
Detect
 ↓
Triage
 ↓
Contain
 ↓
Investigate
 ↓
Mitigate
 ↓
Recover
 ↓
Verify
 ↓
Postmortem
```

#### Failure scenarios

- LLM provider timeout.
- Tool unavailable.
- Retrieval outage.
- Invalid model output.
- Queue backlog.
- Worker crash.
- Cost spike.
- Latency spike.
- Security violation.
- Bad release.

#### Postmortem

- Timeline.
- Impact.
- Root cause.
- Contributing factors.
- Detection.
- Mitigation.
- Corrective actions.
- Regression test.

### Lab --- Production Game Day

Mỗi team nhận một production incident.

Ví dụ: \> Sau release, agent latency tăng 4× và một số requests bị
timeout. Đồng thời tool failure rate tăng.

Học viên phải: 1. Detect bằng dashboard/alert. 2. Trace request. 3.
Identify failure. 4. Decide mitigation. 5. Roll back hoặc hotfix. 6.
Verify recovery. 7. Add regression case. 8. Update runbook.

### Final Deliverables

- Production agent.
- Cloud deployment.
- CI/CD.
- Observability.
- Evaluation.
- Security controls.
- Durable execution.
- Production runbook.
- Incident report.
- Architecture document.
- Improvement backlog.

---

# Cross-Course Capstone

Hai khóa nên sử dụng **cùng một agent project** thay vì tạo project mới
ở mỗi khóa.

## Giai đoạn 1 --- Agent Engineering

```text
User
 ↓
FastAPI
 ↓
Agent Harness
 ├── Context
 ├── Skills
 ├── Memory
 ├── Retrieval
 ├── Tools
 ├── MCP
 ├── Multi-Agent
 ├── Guardrails
 └── Evaluation
```

Sau Buổi 10:

> Agent có thể chạy tốt trong môi trường development nhưng chưa được
> thiết kế đầy đủ cho production operation.

## Giai đoạn 2 --- AgentOps

```text
                    ┌── Langfuse
                    │
User → API → Agent ─┼── OpenTelemetry
          │         │
          │         └── Evaluation
          │
          └→ Queue → Worker
                    │
                    └→ State/Checkpoint

CI/CD
  ↓
Docker
  ↓
Artifact Registry
  ↓
Cloud Run
```

Sau Buổi 20:

> Agent có thể được build, test, evaluate, deploy, observe, optimize và
> operate trong production-oriented environment.

---

# Suggested Teaching Pattern

Mỗi buổi 2 giờ:

Phần Thời lượng Nội dung

---

Concept 20--25 phút Mental model + architecture
Deep dive 25--30 phút Engineering patterns + failure modes
Demo 10--15 phút Instructor code / trace
Lab 45--55 phút Học viên implement
Review 10--15 phút Debug + architecture review

Không nên biến course thành tutorial "copy code". Mỗi buổi nên trả lời 4
câu hỏi:

1. **Why?** --- Vấn đề production nào cần component này?
2. **How?** --- Component được implement như thế nào?
3. **Failure?** --- Nó fail như thế nào?
4. **Evidence?** --- Làm sao biết nó đang hoạt động đúng?

---

# Recommended Project

## Use Case

Có thể dùng một **Operations / Research Agent** xuyên suốt khóa học.

Ví dụ:

> "Operations Intelligence Agent"

Agent có thể: - Search internal knowledge. - Query read-only database. -
Phân tích operational data. - Gọi external API. - Tạo report. - Delegate
research cho subagents. - Nhớ context của user. - Trả citation. -
Streaming progress. - Chạy task dài ở background.

### Agent capabilities

```text
                    Operations Agent
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    Knowledge           Tools             Memory
        │                  │                  │
     Qdrant              MCP             Short-term
        │             ┌────┼────┐         Long-term
        │             │    │    │
        │             DB   API  Files
        │
        └──────────── Context
                           │
                     Agent Loop
                           │
                 ┌─────────┴─────────┐
                 │                   │
             Specialist          Verifier
                 │                   │
                 └─────────┬─────────┘
                           │
                       FastAPI
                           │
                    SSE / Background
```

---

# Assessment Strategy

## Agent Engineering

### 1. Architecture --- 20%

- Correct separation of components.
- Appropriate use of agent vs workflow.
- Clear state boundaries.

### 2. Implementation --- 30%

- Agent loop.
- Tools.
- Retrieval.
- Memory.
- MCP.
- Multi-agent.

### 3. Reliability --- 15%

- Retry.
- Timeout.
- Checkpoint.
- Resume.
- Idempotency.

### 4. Evaluation --- 15%

- Dataset.
- Regression cases.
- Evaluator.
- Evidence.

### 5. Security --- 20%

- Authentication.
- Authorization.
- Tenant isolation.
- Tool permissions.
- Prompt injection defense.
- Audit.

## AgentOps

### 1. Deployment --- 20%

- Docker.
- Cloud Run.
- Secrets.
- IAM.

### 2. CI/CD --- 15%

- Automated test.
- Build.
- Deploy.
- Release/rollback.

### 3. Observability --- 20%

- Logs.
- Metrics.
- Traces.
- Agent traces.

### 4. Continuous Evaluation --- 15%

- Dataset.
- Baseline/candidate.
- Quality gate.

### 5. Performance --- 10%

- Cost.
- Latency.
- Throughput.

### 6. Reliability/Operations --- 20%

- Durable execution.
- Incident response.
- Recovery.
- Runbook.

---

# What Learners Should Know After 20 Sessions

## Agent Engineering

Học viên có thể tự trả lời:

- Agent khác workflow ở đâu?
- Agent loop nên terminate như thế nào?
- State nào cần persist?
- Khi nào cần memory?
- Context nên được build như thế nào?
- Khi nào dùng RAG?
- Retrieval quality đo bằng gì?
- Tool contract nên thiết kế thế nào?
- MCP giải quyết vấn đề gì?
- Khi nào dùng multi-agent?
- Làm sao kiểm thử trajectory?
- Làm sao bảo vệ agent khỏi prompt injection?
- Làm sao isolate data giữa users?
- Làm sao stream agent execution?
- Làm sao đánh giá agent trước khi release?

## AgentOps

Học viên có thể tự trả lời:

- Agent deployment khác API deployment thông thường ở đâu?
- Prompt/model/tool/eval dataset cần versioning thế nào?
- Agent nên chạy synchronous hay background?
- Khi nào cần queue?
- Làm sao resume một task sau worker crash?
- Làm sao correlate API request với agent trace?
- Làm sao phát hiện quality regression?
- Làm sao đo cost theo user/feature/model?
- Làm sao tối ưu latency mà không làm giảm quality?
- Làm sao rollback một agent release?
- Làm sao điều tra production incident?
- Production runbook của agent cần có gì?

---

# Final Architecture

Sau toàn bộ chương trình, architecture mục tiêu:

```text
                         ┌─────────────────────┐
                         │       Client        │
                         └──────────┬──────────┘
                                    │
                              HTTPS / SSE
                                    │
                         ┌──────────▼──────────┐
                         │      FastAPI        │
                         │ Auth / Session      │
                         │ Rate Limit / API    │
                         └──────────┬──────────┘
                                    │
                       ┌────────────▼────────────┐
                       │      Agent Runtime      │
                       │                         │
                       │ Context + Memory        │
                       │ Agent Loop              │
                       │ Skills                  │
                       │ Guardrails              │
                       └─────┬──────┬──────┬─────┘
                             │      │      │
                    ┌────────▼─┐ ┌──▼────┐ ┌▼─────────┐
                    │ Retrieval│ │ Tools │ │Subagents │
                    │  Qdrant  │ │  MCP  │ │          │
                    └──────────┘ └───┬───┘ └──────────┘
                                     │
                               External Systems

              ┌──────────────────────────────────────────┐
              │              AgentOps Layer              │
              │                                          │
              │ Langfuse │ OpenTelemetry │ Grafana       │
              │ Evaluation │ CI/CD │ Docker │ Cloud Run │
              │ Queue │ Workers │ State │ Runbooks      │
              └──────────────────────────────────────────┘
```

# Recommended Outcome

Nếu mục tiêu là đào tạo **AI Engineer / Software Engineer có khả năng
xây agent thực tế**, chương trình nên được hiểu như hai tầng:

**Agent Engineering = xây "brain + harness"**

> Model → Loop → Context → Knowledge → Tools → MCP → Multi-agent →
> Evaluation → Security → API

**AgentOps = biến nó thành "software system có thể vận hành"**

> Repository → API → Docker → Cloud → CI/CD → Observability → Continuous
> Evaluation → Optimization → Durable Execution → Operations

Điểm quan trọng nhất của curriculum là **không dạy 20 công nghệ rời
rạc**. Mỗi buổi phải tiếp tục nâng cấp cùng một agent, để đến cuối khóa
học học viên nhìn thấy rõ quá trình:

```text
LLM
 ↓
Agent
 ↓
Reliable Agent
 ↓
Secure Agent
 ↓
Evaluated Agent
 ↓
API
 ↓
Container
 ↓
Cloud Service
 ↓
Observable Agent
 ↓
Continuously Evaluated Agent
 ↓
Durable Production Agent
```
