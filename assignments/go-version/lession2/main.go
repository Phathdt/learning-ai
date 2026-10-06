// main.go — harness tối giản để thấy rõ ranh giới model/harness
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strings"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/joho/godotenv"
	"github.com/liushuangls/go-anthropic/v2"
)

const (
	MaxTurns    = 10   // budget stop
	CmdTimeout  = 10   // seconds
	MaxOutputKB = 4000 // KB
)

var (
	allowedPrefixes = []string{"ls", "cat", "grep", "wc", "head", "find"} // guardrail thô sơ
)

// Config holds the application configuration
type Config struct {
	APIKey string
	APIURL string
	Model  string
}

// Note: Reusing types from anthropic SDK but implementing custom HTTP client
// This gives us:
// - Type safety from SDK
// - Full control over HTTP layer
// - No SDK version lock-in for API calls

// loadConfig loads configuration from environment variables
func loadConfig() (*Config, error) {
	// Load .env file if exists
	_ = godotenv.Load()

	apiKey := os.Getenv("ANTHROPIC_API_KEY")
	if apiKey == "" {
		return nil, fmt.Errorf("ANTHROPIC_API_KEY not found in environment variables")
	}

	apiURL := os.Getenv("ANTHROPIC_API_URL")
	if apiURL == "" {
		return nil, fmt.Errorf("ANTHROPIC_API_URL not found in environment variables")
	}

	model := os.Getenv("ANTHROPIC_MODEL")
	if model == "" {
		return nil, fmt.Errorf("ANTHROPIC_MODEL not found in environment variables")
	}

	return &Config{
		APIKey: apiKey,
		APIURL: apiURL,
		Model:  model,
	}, nil
}

// runShell executes a shell command with guardrails and error handling
func runShell(command string) string {
	// Check if command is allowed
	allowed := false
	for _, prefix := range allowedPrefixes {
		if strings.HasPrefix(command, prefix) {
			allowed = true
			break
		}
	}

	if !allowed {
		return "ERROR: command not allowed" // tool result handling: lỗi có ngữ nghĩa
	}

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), CmdTimeout*time.Second)
	defer cancel()

	// Execute command
	cmd := exec.CommandContext(ctx, "sh", "-c", command)
	output, err := cmd.CombinedOutput()

	if ctx.Err() == context.DeadlineExceeded {
		return fmt.Sprintf("ERROR: command timeout after %ds", CmdTimeout)
	}

	if err != nil {
		return fmt.Sprintf("ERROR: %v", err)
	}

	// Truncate output to protect context
	outputStr := string(output)
	if len(outputStr) > MaxOutputKB {
		outputStr = outputStr[:MaxOutputKB]
	}

	return outputStr
}

// printJSON prints JSON with pretty formatting, trying jq with color first
func printJSON(data any, label string) {
	if label != "" {
		fmt.Printf("\n%s\n", label)
	}

	jsonBytes, err := json.Marshal(data)
	if err != nil {
		log.Printf("Error marshaling JSON: %v", err)
		return
	}

	// Try using jq for colored output
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "jq", "-C", ".")
	cmd.Stdin = bytes.NewReader(jsonBytes)

	output, err := cmd.CombinedOutput()
	if err == nil && ctx.Err() == nil {
		// jq succeeded, print colored output
		fmt.Print(string(output))
		return
	}

	// jq failed or not available, fallback to native formatting
	var prettyJSON bytes.Buffer
	if err := json.Indent(&prettyJSON, jsonBytes, "", "  "); err != nil {
		log.Printf("Error formatting JSON: %v", err)
		return
	}
	fmt.Println(prettyJSON.String())
}

// callAPI calls the Anthropic API with the given messages using resty
// Uses SDK types but custom HTTP implementation
func callAPI(client *resty.Client, config *Config, messages []anthropic.Message) (*anthropic.MessagesResponse, error) {
	tools := []anthropic.ToolDefinition{
		{
			Name:        "run_shell",
			Description: "Chạy một lệnh shell read-only trong thư mục làm việc. Trả về stdout/stderr.",
			InputSchema: map[string]any{
				"type": "object",
				"properties": map[string]any{
					"command": map[string]string{
						"type": "string",
					},
				},
				"required": []string{"command"},
			},
		},
	}

	req := anthropic.MessagesRequest{
		Model:     anthropic.Model(config.Model),
		MaxTokens: 1024,
		System:    "Bạn là agent phân tích repo. Dùng tool để kiểm chứng trước khi trả lời.",
		Tools:     tools,
		Messages:  messages,
	}

	var resp anthropic.MessagesResponse
	type ErrorResponse struct {
		Type  string `json:"type"`
		Error struct {
			Type    string `json:"type"`
			Message string `json:"message"`
		} `json:"error"`
	}
	var errResp ErrorResponse

	result, err := client.R().
		SetHeader("x-api-key", config.APIKey).
		SetHeader("anthropic-version", "2023-06-01").
		SetHeader("content-type", "application/json").
		SetBody(req).
		SetResult(&resp).
		SetError(&errResp).
		Post("/v1/messages")

	if err != nil {
		return nil, fmt.Errorf("API request failed: %w", err)
	}

	if result.IsError() {
		return nil, fmt.Errorf("API error: %s - %s", errResp.Error.Type, errResp.Error.Message)
	}

	return &resp, nil
}

// agent runs the agent loop with termination conditions
// Uses SDK types for type safety
func agent(client *resty.Client, config *Config, task string) (string, error) {
	messages := []anthropic.Message{
		anthropic.NewUserTextMessage(task),
	} // session state

	for turn := 0; turn < MaxTurns; turn++ {
		printJSON(messages, fmt.Sprintf("=== Turn %d - Messages ===", turn))

		resp, err := callAPI(client, config, messages)
		if err != nil {
			return "", err
		}

		fmt.Printf("\n=== Turn %d - Response ===\nstop=%s | in=%d | out=%d\n",
			turn, resp.StopReason, resp.Usage.InputTokens, resp.Usage.OutputTokens)
		printJSON(resp.Content, "")

		// Add assistant response to messages
		messages = append(messages, anthropic.Message{
			Role:    anthropic.RoleAssistant,
			Content: resp.Content,
		})

		// Check stop reason
		if resp.StopReason != "tool_use" {
			// natural stop
			return resp.GetFirstContentText(), nil
		}

		// Tool execution phase
		var toolResults []anthropic.MessageContent
		for _, content := range resp.Content {
			if content.Type == anthropic.MessagesContentTypeToolUse && content.MessageContentToolUse != nil {
				fmt.Printf("  tool_use %s %v\n", content.MessageContentToolUse.Name, string(content.MessageContentToolUse.Input))

				// Extract command from input using SDK helper
				var input map[string]any
				if err := content.MessageContentToolUse.UnmarshalInput(&input); err != nil {
					log.Printf("Error unmarshaling tool input: %v", err)
					continue
				}

				command, ok := input["command"].(string)
				if !ok {
					log.Printf("Invalid command type in tool input")
					continue
				}

				// Execute tool
				result := runShell(command)

				// Add tool result using SDK helper
				toolResults = append(toolResults, anthropic.NewToolResultMessageContent(
					content.MessageContentToolUse.ID,
					result,
					false,
				))
			}
		}

		// Add tool results to messages (observe)
		messages = append(messages, anthropic.Message{
			Role:    anthropic.RoleUser,
			Content: toolResults,
		})
	}

	return "STOPPED: max turns reached", nil // budget stop
}

func main() {
	// Load configuration
	config, err := loadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Create resty client
	client := resty.New().
		SetBaseURL(config.APIURL).
		SetTimeout(30 * time.Second)

	// Run agent
	task := "Repo này có bao nhiêu file Markdown và file nào dài nhất, ko kiểm tra node_modules?"
	result, err := agent(client, config, task)
	if err != nil {
		log.Fatalf("Agent error: %v", err)
	}

	fmt.Println("\n=== Final Answer ===")
	fmt.Println(result)

	// Alternative task:
	// task := "Liệt kê các file trong thư mục này, sau đó đếm số dòng của file main.go"
}
