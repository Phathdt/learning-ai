# CLAUDE.md — AI Agent Context

> Context file cho AI assistants làm việc với Masterclass Agent Engineering & AgentOps project

## Project Overview

**Loại project:** Educational curriculum — 20-session masterclass về xây dựng và vận hành AI agents

**Mục tiêu:** Tạo tài liệu học tập chi tiết cho khóa Agent Engineering (sessions 1-10) và AgentOps (sessions 11-20), với project xuyên suốt là Operations Intelligence Agent.

**Tech stack:** LangGraph, FastAPI, Qdrant, PostgreSQL, Docker, Google Cloud Run, Langfuse, OpenTelemetry

## Project Structure

```
learning-ai/
├── docs/
│   ├── sessions/              # 20 session documents (001.md - 020.md)
│   │   ├── 001.md             # Modern Agent Systems and Harness
│   │   ├── 002.md             # Agent Loop Engineering with LangGraph
│   │   └── ...
│   └── class/                 # Class materials
├── docs.md                    # Master curriculum outline
├── README.md                  # Project documentation
└── CLAUDE.md                  # This file
```

## Sessions Created (20/20 complete)

All session documents follow consistent structure:

- **Tổng quan** (overview table)
- **Mục tiêu học tập** (measurable learning objectives)
- **Phân bổ thời gian** (time allocation: Concept → Deep dive → Demo → Lab → Review)
- **Theory section** (20-30 min)
- **Deep dive section** (25-35 min)
- **Demo section** (10-15 min with instructor walkthrough)
- **Lab section** (45-50 min with skeleton code)
- **Output/Deliverables**
- **Review questions** (aligned to Why/How/Failure/Evidence framework)
- **References**

### Part I — Agent Engineering (001-010)

| Session | Topic                            | Lines | Key Content                               |
| ------- | -------------------------------- | ----- | ----------------------------------------- |
| 001     | Modern Agent Systems and Harness | 537   | Agent = Model + Harness, 16 components    |
| 002     | Agent Loop with LangGraph        | 934   | State, checkpoint, resume, human approval |
| 003     | Tool and MCP Engineering         | 700+  | MCP architecture, security, auth          |
| 004     | Context Engineering              | 940   | Token budgeting, skills, memory           |
| 005     | Advanced Retrieval               | 850+  | RAG, Qdrant, reranking                    |
| 006     | Multi-Agent Engineering          | 800+  | Patterns, delegation, parallel execution  |
| 007     | Observability and Evaluation     | 850+  | Langfuse, datasets, LLM-as-judge          |
| 008     | Security, Guardrails             | 826   | Threat model, prompt injection defense    |
| 009     | Agent API with FastAPI           | 700+  | SSE streaming, session management         |
| 010     | Build Production-Ready Agent     | 850+  | Capstone integration                      |

### Part II — AgentOps (011-020)

| Session | Topic                             | Lines | Key Content                            |
| ------- | --------------------------------- | ----- | -------------------------------------- |
| 011     | AgentOps: Prototype to Production | 850   | Lifecycle, versioning, reproducibility |
| 012     | Serving with FastAPI              | 850   | Production API patterns                |
| 013     | Containerizing with Docker        | 750+  | Multi-stage build, Docker Compose      |
| 014     | Deploying to Cloud                | 850+  | Google Cloud Run, secrets, IAM         |
| 015     | CI/CD with GitHub Actions         | 780   | Automated pipeline                     |
| 016     | Observability for Agent Systems   | 750+  | Logs, metrics, traces, OTel            |
| 017     | Continuous Evaluation             | 850   | Quality gates, regression suite        |
| 018     | Optimizing Cost and Latency       | 800+  | Bottleneck analysis, trade-offs        |
| 019     | Durable Execution                 | 770   | Message queues, workers, idempotency   |
| 020     | Production Game Day               | 1,050 | Incident response, final capstone      |

**Total:** ~16,000+ lines of documentation

## Document Standards

### Format Conventions

1. **Headers:** Use `#` for title, `##` for major sections, `###` for subsections
2. **Tables:** Use `| --- | --- |` separator style (with spaces)
3. **Code blocks:** Always specify language (`python,`bash, ```text)
4. **Vietnamese:** All explanations in Vietnamese, technical terms in English
5. **Time blocks:** Concept (20-25 phút) → Deep dive (25-35 phút) → Demo (10-15 phút) → Lab (45-50 phút) → Review (10-15 phút)

### Code Requirements

- All Python code must be syntactically valid (validated with `ast.parse`)
- Include full working examples, not just snippets
- Skeleton code should be 200-600 lines for labs
- Use descriptive variable names, include comments
- Follow PEP 8 for Python

### Learning Framework

Every session answers 4 questions:

1. **Why?** — Vấn đề production nào cần component này?
2. **How?** — Component được implement như thế nào?
3. **Failure?** — Nó fail như thế nào?
4. **Evidence?** — Làm sao biết nó đang hoạt động đúng?

## Key Concepts

### Agent = Model + Harness

- **Model:** LLM (Claude, GPT)
- **Harness:** Mọi thứ còn lại (16 components)
  1. System prompt/instructions
  2. Context builder
  3. Conversation/session state
  4. Tools
  5. Tool result handling
  6. Memory
  7. Skills
  8. Retrieval
  9. Execution environment
  10. Guardrails
  11. Human approval
  12. Persistence/checkpoint
  13. Observability
  14. Evaluation
  15. Orchestration/subagents
  16. Model selection

### The Agent Loop

```
Observe → Decide → Act → Verify → (repeat or terminate)
```

### Termination Conditions

- Natural stop (model ends conversation)
- Budget stop (max turns, tokens, cost, time)
- Goal stop (verifier confirms success)
- Safety stop (guardrail blocks action)
- Error stop (unrecoverable failure)

## Working with This Project

### When adding new content

1. **Check existing sessions** — Maintain consistency with 001-020 structure
2. **Reference curriculum** — `docs.md` is the source of truth
3. **Validate Python** — All code blocks must parse correctly
4. **Use Vietnamese** — Explanations in Vietnamese, code/tech terms in English
5. **Include references** — Link to external docs, papers, tools

### When modifying sessions

1. **Read existing content first** — Understand current structure
2. **Preserve format** — Keep table formatting, headers, time allocations
3. **Update cross-references** — If changing one session, check related sessions
4. **Test code examples** — Ensure syntax validity

### Common patterns

#### Overview table format

```markdown
| Hạng mục           | Nội dung                      |
| ------------------ | ----------------------------- |
| Đầu vào            | Prerequisites                 |
| Đầu ra             | Deliverables                  |
| Công cụ            | Tools/libraries               |
| Project xuyên suốt | Operations Intelligence Agent |
```

#### Learning objectives format

```markdown
### Mục tiêu học tập (đo được)

Sau buổi học, học viên có thể:

1. [Verb] [measurable outcome]
2. [Verb] [measurable outcome]
   ...
```

#### Lab structure

```markdown
### 4.1 Chuẩn bị

### 4.2 Bài tập chính

### 4.3 Skeleton code

### 4.4 Các bước thực hiện

### 4.5 Thí nghiệm failure mode (bắt buộc)

### 4.6 Nâng cao (tùy chọn)
```

## Operations Intelligence Agent

**Project xuyên suốt** qua 20 sessions:

- **Sessions 1-3:** Khung cơ bản (loop, state, tools)
- **Sessions 4-5:** Context + retrieval
- **Session 6:** Multi-agent capabilities
- **Sessions 7-8:** Evaluation + security
- **Session 9:** API layer
- **Session 10:** Integration capstone
- **Sessions 11-15:** Deployment pipeline
- **Sessions 16-18:** Observability + optimization
- **Sessions 19-20:** Durable execution + operations

## References

### Key Technologies

- **LangGraph:** State machine framework cho agents — [docs.langchain.com/langgraph](https://docs.langchain.com/oss/python/langgraph/)
- **Anthropic Claude:** Primary LLM — [docs.anthropic.com](https://docs.anthropic.com/)
- **MCP (Model Context Protocol):** Tool integration — [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Qdrant:** Vector database — [qdrant.tech](https://qdrant.tech/)
- **Langfuse:** Agent observability — [langfuse.com](https://langfuse.com/)
- **FastAPI:** Python web framework — [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)

### Key Papers & Articles

- Anthropic: "Building Effective Agents" — [anthropic.com/engineering/building-effective-agents](https://www.anthropic.com/engineering/building-effective-agents)
- arXiv 2609.00006: "Harness Engineering" — [arxiv.org/html/2609.00006](https://arxiv.org/html/2609.00006)

## Development Workflow

### Creating new sessions (if needed)

1. Read `docs.md` for curriculum outline
2. Reference existing sessions (001.md, 002.md) for structure
3. Research topic deeply (external sources)
4. Write theory + deep dive sections
5. Create working code examples
6. Design hands-on lab with skeleton code
7. Validate all Python syntax
8. Add references

### Maintaining quality

- **Consistency:** All sessions follow same format
- **Completeness:** Theory → Practice → Verification
- **Practicality:** Working code, not pseudocode
- **Evidence-based:** Cite sources, link to docs
- **Vietnamese quality:** Full diacritics, proper grammar

## Status

✅ **Project complete:** All 20 sessions created  
✅ **Documentation:** README.md + CLAUDE.md  
✅ **Quality:** All Python code validated  
✅ **Structure:** Consistent format across sessions

**Next steps (if needed):**

- Add example code directory (`examples/`)
- Add lab solutions directory (`labs/`)
- Create slide decks (`docs/class/`)
- Record video walkthroughs
- Build student assessment rubrics

## DO

- ✅ Keep Vietnamese explanations clear and technical
- ✅ Validate all code syntax before writing
- ✅ Reference external sources
- ✅ Build on previous sessions
- ✅ Include failure modes and evidence
- ✅ Provide complete working examples

## DON'T

- ❌ Create sessions outside `docs/sessions/`
- ❌ Use inconsistent table formatting
- ❌ Write pseudocode instead of working code
- ❌ Skip learning objectives or deliverables
- ❌ Forget to link sessions together
- ❌ Translate technical terms to Vietnamese

---

**For AI assistants:** This project teaches production agent engineering. Focus on **harness** (system around LLM), not just prompts. Every component needs: Why/How/Failure/Evidence.
