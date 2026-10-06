# So sánh 3 phiên bản: Python vs Node.js vs Go

## Tổng quan

| Tiêu chí | Python | Node.js/TypeScript | Go |
|----------|--------|-------------------|-----|
| **Ngôn ngữ** | Python 3.13 | TypeScript + Node.js 18+ | Go 1.23+ |
| **Package Manager** | uv | pnpm | go modules |
| **HTTP Client** | httpx (sync) | axios | resty |
| **API Wrapper** | Không (raw HTTP) | Không (raw HTTP) | Không (raw HTTP) |
| **Type Safety** | Runtime (optional typing) | Compile-time | Compile-time |
| **Concurrency** | Synchronous | async/await | Goroutines (chưa dùng) |
| **Binary Size** | N/A (interpreted) | N/A (interpreted) | ~9.6MB |
| **Startup Time** | ~100-200ms | ~200-500ms | <10ms |
| **Memory Usage** | ~40-60MB | ~50-80MB | ~15-30MB |

## Cấu trúc code tương đồng

Cả 3 version đều implement **agent loop** giống nhau:

```
Observe → Decide → Act (tool execution) → Verify → (repeat hoặc terminate)
```

### 1. Termination Conditions

| Condition | Python | Node.js | Go |
|-----------|--------|---------|-----|
| Natural stop | ✅ `stop_reason != "tool_use"` | ✅ `stop_reason !== "tool_use"` | ✅ `stop_reason != "tool_use"` |
| Budget stop | ✅ `MAX_TURNS = 10` | ✅ `MAX_TURNS = 10` | ✅ `MaxTurns = 10` |
| Goal stop | ❌ (chưa implement) | ❌ (chưa implement) | ❌ (chưa implement) |
| Safety stop | ❌ (chưa implement) | ❌ (chưa implement) | ❌ (chưa implement) |
| Error stop | ❌ (chưa implement) | ❌ (chưa implement) | ❌ (chưa implement) |

### 2. Tool Execution Guardrails

Cả 3 version đều có **whitelist commands**:

```python
ALLOWED_PREFIXES = ["ls", "cat", "grep", "wc", "head", "find"]
```

```typescript
const ALLOWED_PREFIXES = ["ls", "cat", "grep", "wc", "head", "find"] as const;
```

```go
allowedPrefixes = []string{"ls", "cat", "grep", "wc", "head", "find"}
```

### 3. Error Handling

| Error Type | Python | Node.js | Go |
|------------|--------|---------|-----|
| Command not allowed | ✅ | ✅ | ✅ |
| Timeout (10s) | ✅ | ✅ | ✅ |
| Output truncation (4000 chars) | ✅ | ✅ | ✅ |
| API errors | ✅ | ✅ | ✅ |

### 4. Session State Management

Tất cả đều sử dụng **messages array** để lưu lịch sử:

- **Python**: `messages: list[dict]`
- **Node.js**: `messages: MessageParam[]`
- **Go**: `messages []Message`

## Sự khác biệt chính

### 1. Type System

**Python** (runtime typing):
```python
def run_shell(command: str) -> str:
    # Type hints chỉ là gợi ý, không enforce
```

**TypeScript** (compile-time):
```typescript
async function runShell(command: string): Promise<string> {
    // Compiler check types
}
```

**Go** (compile-time + strict):
```go
func runShell(command string) string {
    // Strict type checking
}
```

### 2. Error Handling Pattern

**Python**:
```python
try:
    result = subprocess.run(cmd, ...)
except subprocess.TimeoutExpired:
    return "ERROR: timeout"
except Exception as e:
    return f"ERROR: {e}"
```

**Node.js**:
```typescript
try {
    const { stdout, stderr } = await execAsync(command, { timeout: 10000 });
} catch (error: any) {
    if (error.killed) return "ERROR: timeout";
    return `ERROR: ${error.message}`;
}
```

**Go**:
```go
ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
defer cancel()
cmd := exec.CommandContext(ctx, "sh", "-c", command)
if ctx.Err() == context.DeadlineExceeded {
    return "ERROR: timeout"
}
```

### 3. JSON Formatting

**Python** (jq fallback):
```python
try:
    subprocess.run(["jq", "-C", "."], input=json_str.encode(), check=True)
except (FileNotFoundError, subprocess.CalledProcessError):
    print(json.dumps(data, indent=2))
```

**Node.js** (jq fallback):
```typescript
try {
    const { stdout } = await execAsync(`echo '${jsonStr}' | jq -C .`);
    console.log(stdout);
} catch {
    console.log(JSON.stringify(data, null, 2));
}
```

**Go** (native only):
```go
jsonBytes, _ := json.MarshalIndent(data, "", "  ")
fmt.Println(string(jsonBytes))
```

### 4. HTTP Client

**Python** (httpx):
```python
import httpx

response = httpx.post(
    f"{API_URL}/v1/messages",
    headers={"x-api-key": API_KEY, ...},
    json=payload,
    timeout=30.0,
)
```

**Node.js** (axios):
```typescript
import axios from "axios";

const client = axios.create({
    baseURL: `${API_URL}/v1`,
    headers: { "x-api-key": API_KEY, ... },
});
const response = await client.post("/messages", payload);
```

**Go** (resty):
```go
import "github.com/go-resty/resty/v2"

client := resty.New().SetBaseURL(config.APIURL)
resp, err := client.R().
    SetHeader("x-api-key", config.APIKey).
    SetBody(req).
    Post("/v1/messages")
```

## Performance Comparison

### Startup Time

```
Go:         < 10ms  ████
Node.js:    ~300ms  ████████████████████████████████
Python:     ~150ms  ███████████████
```

### Memory Usage (idle)

```
Go:         ~20MB   ████████
Node.js:    ~65MB   ██████████████████████████
Python:     ~50MB   ████████████████████
```

### Binary/Deployment

| | Python | Node.js | Go |
|---|--------|---------|-----|
| **Runtime required** | ✅ Python 3.13+ | ✅ Node.js 18+ | ❌ None |
| **Dependencies** | ✅ Install via uv | ✅ npm/pnpm install | ❌ Compiled in |
| **Deploy size** | ~50MB (venv) | ~100MB (node_modules) | ~10MB (single binary) |
| **Cross-platform** | ⚠️ Need Python | ⚠️ Need Node.js | ✅ Compile for target |

## Code Complexity

### Lines of Code (excluding comments/blanks)

```
Python:     ~145 lines
Node.js:    ~155 lines
Go:         ~320 lines (verbose type definitions)
```

### Cognitive Complexity

- **Python**: Thấp nhất (đơn giản, ít boilerplate)
- **Node.js**: Trung bình (async/await, type definitions)
- **Go**: Cao nhất (verbose error handling, explicit types)

## Khi nào dùng version nào?

### Chọn Python khi:
- Prototype nhanh
- Team quen Python
- Ecosystem AI/ML (nhiều library)
- Script automation
- Jupyter notebook

### Chọn Node.js/TypeScript khi:
- Web integration (frontend/backend)
- npm ecosystem lớn
- Team JavaScript
- Real-time (WebSocket)
- Serverless functions

### Chọn Go khi:
- Production deployment (single binary)
- Performance critical
- Low memory footprint
- Long-running services
- CLI tools distribution
- Cloud-native (Kubernetes, Docker)

## Kết luận

Cả 3 version đều implement **cùng một agent harness pattern**:

1. ✅ Agent loop với termination conditions
2. ✅ Tool execution với guardrails
3. ✅ Session state management
4. ✅ Error handling
5. ✅ JSON formatting
6. ✅ Type safety (runtime hoặc compile-time)

**Khác biệt chính:**
- **Python**: Đơn giản, nhanh prototype
- **Node.js**: Web-friendly, async native
- **Go**: Fast, efficient, single binary

**Tất cả đều cho thấy:** Agent = Model + Harness, và harness chiếm phần lớn logic!
