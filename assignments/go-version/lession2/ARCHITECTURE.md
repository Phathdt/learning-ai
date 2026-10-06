# Architecture: Hybrid Approach

## SDK Types + Custom HTTP Client

Go version sử dụng **hybrid approach** để kết hợp ưu điểm của cả SDK và custom implementation.

### What We Use from SDK

```go
import "github.com/liushuangls/go-anthropic/v2"

// 1. Type definitions
type Message = anthropic.Message
type MessageContent = anthropic.MessageContent
type MessagesRequest = anthropic.MessagesRequest
type MessagesResponse = anthropic.MessagesResponse

// 2. Constants
anthropic.RoleUser
anthropic.RoleAssistant
anthropic.MessagesContentTypeToolUse

// 3. Helper functions
anthropic.NewUserTextMessage(task)
anthropic.NewToolResultMessageContent(id, result, false)

// 4. Utility methods
content.MessageContentToolUse.UnmarshalInput(&input)
resp.GetFirstContentText()
```

### What We Don't Use from SDK

```go
// ❌ NOT using SDK's HTTP client
// client := anthropic.NewClient(apiKey)
// resp, err := client.CreateMessages(ctx, req)

// ✅ Using custom resty HTTP client
client := resty.New().SetBaseURL(config.APIURL)
resp, err := client.R().
    SetHeader("x-api-key", config.APIKey).
    SetBody(req).
    Post("/v1/messages")
```

## Benefits of This Approach

### 1. Type Safety
```go
// Compile-time type checking
messages := []anthropic.Message{
    anthropic.NewUserTextMessage(task),  // ✅ Type-safe
}

// vs manual types
messages := []Message{
    {Role: "user", Content: ...},  // ⚠️ String literals, typo-prone
}
```

### 2. SDK Helper Functions
```go
// Clean and readable
toolResult := anthropic.NewToolResultMessageContent(
    toolUseID,
    result,
    false,
)

// vs manual construction
toolResult := MessageContent{
    Type:      "tool_result",
    ToolUseID: &toolUseID,
    Content:   []MessageContent{{Type: "text", Text: &result}},
    IsError:   &isError,
}
```

### 3. Full HTTP Control
```go
// Custom timeout, retries, interceptors
client := resty.New().
    SetBaseURL(config.APIURL).
    SetTimeout(30 * time.Second).
    SetRetryCount(3).
    OnBeforeRequest(func(c *resty.Client, r *resty.Request) error {
        log.Printf("Making request to: %s", r.URL)
        return nil
    })

// Easy to add custom headers, debugging, metrics
result, err := client.R().
    SetHeader("x-custom-header", "value").
    SetBody(req).
    SetResult(&resp).
    Post("/v1/messages")
```

### 4. No SDK Version Lock-in
```
✅ API changes? Update types, keep HTTP logic
✅ SDK has bugs? Bypass with custom HTTP
✅ Need custom behavior? Full control
❌ Stuck with SDK's retry logic
❌ SDK doesn't support feature X
```

## Comparison with Other Approaches

### Approach 1: Pure SDK
```go
client := anthropic.NewClient(apiKey)
resp, err := client.CreateMessages(ctx, req)
```
**Pros:** Simple, works out of box  
**Cons:** Less control, SDK version lock-in, harder to debug

### Approach 2: Pure Custom (như trước)
```go
// Define all types manually
type Message struct {
    Role    string `json:"role"`
    Content []MessageContent `json:"content"`
}
```
**Pros:** Full control  
**Cons:** More code, manual type definitions, no helpers

### Approach 3: Hybrid (current) ⭐
```go
// Use SDK types
messages := []anthropic.Message{...}

// Custom HTTP
client.R().SetBody(req).Post("/v1/messages")
```
**Pros:** Type safety + control + helpers  
**Cons:** Two dependencies (minimal overhead)

## Implementation Pattern

```go
// 1. Import SDK for types only
import "github.com/liushuangls/go-anthropic/v2"

// 2. Create custom HTTP client
client := resty.New().SetBaseURL(apiURL)

// 3. Use SDK types in function signatures
func callAPI(client *resty.Client, messages []anthropic.Message) (*anthropic.MessagesResponse, error)

// 4. Build request with SDK types
req := anthropic.MessagesRequest{
    Model:     anthropic.Model(config.Model),
    MaxTokens: 1024,
    Messages:  messages,
}

// 5. Call API with custom HTTP
var resp anthropic.MessagesResponse
result, err := client.R().
    SetBody(req).
    SetResult(&resp).
    Post("/v1/messages")

// 6. Use SDK helper methods
for _, content := range resp.Content {
    if content.Type == anthropic.MessagesContentTypeToolUse {
        content.MessageContentToolUse.UnmarshalInput(&input)
    }
}
```

## Real-World Benefits

### Debugging
```go
// Add logging middleware
client.OnAfterResponse(func(c *resty.Client, r *resty.Response) error {
    log.Printf("Status: %d, Time: %v", r.StatusCode(), r.Time())
    return nil
})
```

### Retry Logic
```go
client.SetRetryCount(3).
    SetRetryWaitTime(1 * time.Second).
    AddRetryCondition(func(r *resty.Response, err error) bool {
        return r.StatusCode() == 429  // Rate limit
    })
```

### Custom Headers
```go
client.R().
    SetHeader("x-custom-id", requestID).
    SetHeader("x-trace-id", traceID).
    Post("/v1/messages")
```

### Testing
```go
// Easy to mock HTTP layer
mockClient := resty.New().SetBaseURL("http://localhost:8080")
// vs mocking SDK's internal HTTP client
```

## Conclusion

**Hybrid approach = Best of both worlds:**
1. ✅ Type safety from SDK
2. ✅ Helper functions from SDK
3. ✅ Full HTTP control
4. ✅ Easy debugging/testing
5. ✅ No lock-in

**This is the recommended approach for production Go applications using external APIs.**
