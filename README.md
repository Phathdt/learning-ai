# Masterclass Agent Engineering & AgentOps

> **Khóa học toàn diện về xây dựng AI agents production-ready từ cơ bản đến vận hành**
>
> 20 buổi × 2 giờ | Lý thuyết + Thực hành | Từ prototype đến production

## Giới thiệu

Khóa học này hướng dẫn chi tiết cách xây dựng, đánh giá, bảo mật và vận hành AI agents trong môi trường production. Khác với các khóa chỉ dừng ở prompt engineering, chúng ta đi sâu vào **harness engineering** — thiết kế hệ thống bao quanh LLM để biến nó thành một công cụ làm việc thực sự.

**Project xuyên suốt:** Operations Intelligence Agent — một agent có khả năng truy vấn database, phân tích dữ liệu, và tạo báo cáo thông minh.

## Cấu trúc khóa học

### Phần I — Agent Engineering (Buổi 1-10)

Xây dựng agent từ khái niệm cơ bản đến production-ready:

| Buổi                        | Chủ đề                                  | Nội dung chính                                                  |
| --------------------------- | --------------------------------------- | --------------------------------------------------------------- |
| [001](docs/sessions/001.md) | Modern Agent Systems and Harness        | Agent = Model + Harness, anatomy của agent loop, trust boundary |
| [002](docs/sessions/002.md) | Agent Loop Engineering with LangGraph   | State, checkpoint, resume, human approval, retry                |
| [003](docs/sessions/003.md) | Tool and MCP Engineering                | Tool design, MCP architecture, security, authentication         |
| [004](docs/sessions/004.md) | Context Engineering                     | Token budgeting, skills, memory, multi-user isolation           |
| [005](docs/sessions/005.md) | Advanced Retrieval and Vector Databases | RAG, Qdrant, chunking, reranking, multi-tenant retrieval        |
| [006](docs/sessions/006.md) | Multi-Agent Engineering                 | Patterns, delegation, parallel execution, conflict resolution   |
| [007](docs/sessions/007.md) | Observability and Evaluation            | Langfuse, evaluation dimensions, dataset design, LLM-as-judge   |
| [008](docs/sessions/008.md) | Security, Guardrails and Governance     | Threat model, prompt injection, guardrails, audit               |
| [009](docs/sessions/009.md) | Agent API Engineering with FastAPI      | API contract, SSE streaming, session management                 |
| [010](docs/sessions/010.md) | Build Your Production-Ready Agent       | Capstone: tổng hợp tất cả components                            |

### Phần II — AgentOps (Buổi 11-20)

Vận hành agent như production system:

| Buổi                        | Chủ đề                                 | Nội dung chính                                                |
| --------------------------- | -------------------------------------- | ------------------------------------------------------------- |
| [011](docs/sessions/011.md) | AgentOps: From Prototype to Production | Lifecycle, versioning, dependency management, reproducibility |
| [012](docs/sessions/012.md) | Serving an Agent with FastAPI          | Production API patterns, middleware, structured logging       |
| [013](docs/sessions/013.md) | Containerizing Agents with Docker      | Multi-stage build, Docker Compose, health checks              |
| [014](docs/sessions/014.md) | Deploying to Cloud                     | Google Cloud Run, secrets, IAM, rollback                      |
| [015](docs/sessions/015.md) | CI/CD with GitHub Actions              | Automated testing, build pipeline, deployment automation      |
| [016](docs/sessions/016.md) | Observability for Agent Systems        | Logs, metrics, traces, OpenTelemetry, correlation             |
| [017](docs/sessions/017.md) | Continuous Evaluation with Langfuse    | AI Engineering Loop, quality gates, regression suite          |
| [018](docs/sessions/018.md) | Optimizing Cost and Latency            | Bottleneck analysis, trade-offs, AI Gateway                   |
| [019](docs/sessions/019.md) | Durable Execution and High Throughput  | Message queues, workers, checkpoint recovery, idempotency     |
| [020](docs/sessions/020.md) | Production Game Day and Final Project  | Incident response, postmortem, capstone deliverables          |

## Learning Path

```text
Understand → Build → Context → Knowledge → Tools → Coordinate →
Evaluate → Secure → Serve → Deliver → Prepare → Containerize →
Deploy → Automate → Observe → Evaluate Continuously → Optimize →
Run Durably → Operate
```

## Điều kiện tiên quyết

- Python 3.11+
- Hiểu cơ bản về LLM API (từng gọi OpenAI/Anthropic API)
- Git, terminal, Docker basics
- Có thẻ thanh toán để trả API (chi phí ước tính: $20-50 cho toàn khóa)

## Công cụ & Tech Stack

| Layer               | Technologies                        |
| ------------------- | ----------------------------------- |
| **LLM**             | Claude (Anthropic), OpenAI          |
| **Agent Framework** | LangGraph, Anthropic SDK            |
| **Tools & MCP**     | MCP protocol, custom tools          |
| **Database**        | PostgreSQL, SQLite                  |
| **Vector DB**       | Qdrant                              |
| **API**             | FastAPI, Pydantic, SSE              |
| **Observability**   | Langfuse, OpenTelemetry, Grafana    |
| **Container**       | Docker, Docker Compose              |
| **Cloud**           | Google Cloud Run, Artifact Registry |
| **CI/CD**           | GitHub Actions                      |
| **Queue**           | Redis Streams, PostgreSQL           |

## Cài đặt

```bash
# Clone repository
git clone <repo-url>
cd learning-ai

# Cài dependencies (nếu có)
pip install -r requirements.txt  # hoặc
pnpm install

# Cấu hình API keys
cp .env.example .env
# Edit .env với keys của bạn

# Chạy demo đầu tiên (từ session 001)
python docs/sessions/examples/minimal_agent.py
```

## Cấu trúc thư mục

```
learning-ai/
├── docs/
│   ├── sessions/          # 20 session documents
│   │   ├── 001.md         # Buổi 1: Modern Agent Systems
│   │   ├── 002.md         # Buổi 2: Agent Loop with LangGraph
│   │   └── ...
│   └── class/             # Class materials, slides
├── examples/              # Code examples từ các buổi học
├── labs/                  # Lab exercises
├── plans/                 # Implementation plans
└── README.md
```

## Sessions tham khảo nhanh

**Nếu bạn muốn:**

- Hiểu agent là gì → [Session 001](docs/sessions/001.md)
- Xây agent loop có state → [Session 002](docs/sessions/002.md)
- Thiết kế tools an toàn → [Session 003](docs/sessions/003.md)
- Quản lý context & token → [Session 004](docs/sessions/004.md)
- Build RAG với vector DB → [Session 005](docs/sessions/005.md)
- Orchestrate nhiều agents → [Session 006](docs/sessions/006.md)
- Đánh giá agent quality → [Session 007](docs/sessions/007.md)
- Bảo mật agent → [Session 008](docs/sessions/008.md)
- Serve qua API → [Sessions 009, 012](docs/sessions/009.md)
- Deploy lên cloud → [Sessions 013-015](docs/sessions/013.md)
- Monitor & optimize → [Sessions 016-018](docs/sessions/016.md)
- Vận hành production → [Sessions 019-020](docs/sessions/019.md)

## 4 câu hỏi trung tâm

Mỗi session trả lời 4 câu hỏi:

1. **Why?** — Tại sao cần component này?
2. **How?** — Implement như thế nào?
3. **Failure?** — Fail modes là gì?
4. **Evidence?** — Làm sao biết nó đang hoạt động đúng?

## Deliverables cuối khóa

Sau 20 buổi, học viên có:

✅ **Production agent** — Operations Intelligence Agent hoàn chỉnh  
✅ **Architecture diagram** — System design document  
✅ **Cloud deployment** — Running trên Google Cloud Run  
✅ **CI/CD pipeline** — Automated testing & deployment  
✅ **Observability** — Logs, metrics, traces với Langfuse + OTel  
✅ **Evaluation system** — Golden dataset + quality gates  
✅ **Security controls** — Threat model + guardrails + audit  
✅ **Durable execution** — Queue-based background processing  
✅ **Production runbook** — Incident response procedures  
✅ **Improvement backlog** — P0/P1/P2 items cho next iteration

## Đóng góp

Project này là tài liệu học tập. Nếu phát hiện lỗi hoặc có đề xuất cải tiến:

1. Tạo issue mô tả vấn đề
2. Hoặc tạo PR với fix/improvement
3. Tuân thủ format markdown hiện tại

## License

[Specify license here]

## Liên hệ

- **Instructor:** [Name]
- **Email:** [Email]
- **Discussion:** [Link to forum/Discord/Slack]

---

**Lưu ý quan trọng:**

> Khóa học này tập trung vào **harness engineering** — việc xây dựng hệ thống bao quanh LLM. Model chỉ là một trong 16 components. Phần lớn công việc nằm ở: state management, tool design, context engineering, security, observability, và operations.

**Bắt đầu ngay:** [Session 001 - Modern Agent Systems and Harness](docs/sessions/001.md)
