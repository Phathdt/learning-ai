# LLM App (Go)

Simple Go application để gọi LLM API sử dụng Anthropic Claude.

## Cài đặt

1. Clone repository này
2. Cài đặt dependencies:
   ```bash
   go mod download
   ```

3. Tạo file `.env` từ template:
   ```bash
   cp .env.example .env
   ```

4. Cập nhật `.env` với API key của bạn:
   ```
   ANTHROPIC_API_KEY=your_actual_api_key
   ANTHROPIC_API_URL=https://api.anthropic.com
   ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
   ```

## Sử dụng

### Development mode (với go run)
```bash
go run main.go
```

### Build binary
```bash
go build -o lession2
./lession2
```

### Run với live reload (cần air)
```bash
# Cài đặt air nếu chưa có
go install github.com/air-verse/air@latest

# Chạy với air
air
```

## Cấu trúc

- `main.go`: File chính chứa logic gọi LLM API
- `go.mod`: Module definition và dependencies
- `.env.example`: Template cho environment variables
- `.env`: File chứa API key (không commit vào git)
- `README.md`: File hướng dẫn này

## Dependencies

- `github.com/go-resty/resty/v2`: Go HTTP client (tương tự axios trong Node.js)
- `github.com/liushuangls/go-anthropic/v2`: Anthropic SDK - **chỉ dùng type definitions**
- `github.com/joho/godotenv`: Load environment variables từ file .env
- `jq` (optional): JSON formatter với color output

### Hybrid Approach: SDK Types + Custom HTTP

Project này sử dụng **best of both worlds**:

1. ✅ **Reuse SDK types**: `anthropic.Message`, `anthropic.MessageContent`, `anthropic.MessagesRequest`, etc.
2. ✅ **Custom HTTP client**: Tự implement REST calls với `resty`
3. ✅ **Helper functions**: Sử dụng SDK helpers như `NewUserTextMessage()`, `NewToolResultMessageContent()`

**Tại sao approach này tốt?**
- Type safety từ SDK (compile-time checking)
- Full control over HTTP layer (debugging, retries, custom headers)
- Không bị lock-in vào SDK implementation
- Dễ customize request/response handling

## Yêu cầu hệ thống

- Go >= 1.23
- Unix-like shell (Linux/macOS) hoặc WSL trên Windows

## So sánh với Node.js/TypeScript version

Phiên bản Go này có các tính năng tương đương:

1. **Agent loop** với termination conditions (natural stop, budget stop)
2. **Tool execution** với guardrails (chỉ cho phép read-only commands)
3. **Session state** management với messages array
4. **Error handling** cho tool execution và timeout
5. **JSON formatting** với pretty print
6. **Strongly typed** với Go type system

### Khác biệt chính:

- Sử dụng `context.Context` cho timeout và cancellation
- Statically compiled binary (không cần runtime)
- Type safety với Go's strong typing
- Goroutines potential cho concurrent operations (chưa sử dụng trong version này)
- Error handling với explicit error returns
- **REST client với resty** (tương tự axios, không dùng SDK)
- **JSON formatting với jq color fallback** (tương tự Python/Node.js)

### Performance:

- **Startup time**: Go binary nhanh hơn nhiều (milliseconds vs hundreds of ms)
- **Memory usage**: Go thường dùng ít memory hơn Node.js
- **Binary size**: Single binary không cần dependencies runtime
- **Deployment**: Copy binary là đủ, không cần install runtime

## Các tính năng

### 1. Agent Loop
- Maximum 10 turns (configurable)
- Natural stop khi model kết thúc
- Budget stop khi đạt max turns

### 2. Tool Execution
- Guardrails: Chỉ cho phép read-only commands (ls, cat, grep, wc, head, find)
- Timeout: 10 seconds per command
- Output truncation: 4000KB max
- Error handling: Timeout, permission, execution errors

### 3. Session State
- Messages history tracking
- Tool use và tool result correlation
- Context preservation across turns

### 4. Safety Features
- Command whitelist
- Timeout protection
- Output size limits
- Error propagation

## Ví dụ tasks

```go
// Task 1: Đếm files và tìm file dài nhất
task := "Repo này có bao nhiêu file Markdown và file nào dài nhất, ko kiểm tra node_modules?"

// Task 2: List files và đếm dòng
task := "Liệt kê các file trong thư mục này, sau đó đếm số dòng của file main.go"

// Task 3: Tìm kiếm pattern
task := "Tìm tất cả các function definitions trong các file .go"
```

## Troubleshooting

### API Key not found
```
ANTHROPIC_API_KEY not found in environment variables
```
→ Check `.env` file exists và có ANTHROPIC_API_KEY

### Command not allowed
```
ERROR: command not allowed
```
→ Command không nằm trong whitelist. Chỉ cho phép: ls, cat, grep, wc, head, find

### Timeout error
```
ERROR: command timeout after 10s
```
→ Command chạy quá lâu. Consider optimizing hoặc tăng CmdTimeout constant

## License

MIT
