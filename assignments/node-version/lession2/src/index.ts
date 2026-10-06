// minimal_agent.ts — harness tối giản để thấy rõ ranh giới model/harness
import type {
  MessageParam,
  Message as AnthropicMessage,
  Tool,
  TextBlock,
  ToolUseBlock,
} from "@anthropic-ai/sdk/resources/messages.mjs";
import axios, { AxiosInstance } from "axios";
import { exec } from "child_process";
import { promisify } from "util";
import { config } from "dotenv";

const execAsync = promisify(exec);

// Load environment variables from .env file
config();

// Get configuration from environment variables
const API_KEY = process.env.ANTHROPIC_API_KEY;
const API_URL = process.env.ANTHROPIC_API_URL;
const MODEL = process.env.ANTHROPIC_MODEL || "";

if (!API_KEY) {
  throw new Error("ANTHROPIC_API_KEY not found in environment variables");
}
if (!API_URL) {
  throw new Error("ANTHROPIC_API_URL not found in environment variables");
}
if (!MODEL) {
  throw new Error("ANTHROPIC_MODEL not found in environment variables");
}

// Axios client with custom headers
const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_URL}/v1`,
  headers: {
    "x-api-key": API_KEY,
    "anthropic-version": "2023-06-01",
    "content-type": "application/json",
  },
});

const MAX_TURNS = 10; // budget stop

const TOOLS: Tool[] = [
  {
    name: "run_shell",
    description:
      "Chạy một lệnh shell read-only trong thư mục làm việc. Trả về stdout/stderr.",
    input_schema: {
      type: "object",
      properties: {
        command: { type: "string" },
      },
      required: ["command"],
    },
  },
];

const ALLOWED_PREFIXES = ["ls", "cat", "grep", "wc", "head", "find"] as const; // guardrail thô sơ

/**
 * Tool execution với guardrails và error handling
 */
async function runShell(command: string): Promise<string> {
  const isAllowed = ALLOWED_PREFIXES.some((prefix) =>
    command.startsWith(prefix)
  );

  if (!isAllowed) {
    return "ERROR: command not allowed"; // tool result handling: lỗi có ngữ nghĩa
  }

  try {
    const { stdout, stderr } = await execAsync(command, {
      timeout: 10000,
      maxBuffer: 4000 * 1024,
    });
    const output = (stdout + stderr).slice(0, 4000); // cắt ngắn để bảo vệ context
    return output;
  } catch (error: any) {
    if (error.killed) {
      return "ERROR: command timeout after 10s";
    }
    return `ERROR: ${error.message}`;
  }
}

/**
 * Print JSON với jq nếu available, fallback về JSON.stringify
 */
async function printJson(data: unknown, label: string = ""): Promise<void> {
  const jsonStr = JSON.stringify(data, null, 0);

  try {
    // Try using jq for pretty formatting with color
    const { stdout } = await execAsync(
      `echo '${jsonStr.replace(/'/g, "'\\''")}' | jq -C .`,
      {
        timeout: 2000,
      }
    );
    if (label) {
      console.log(`\n${label}`);
    }
    console.log(stdout);
  } catch {
    // jq not available or error, use JSON.stringify
    if (label) {
      console.log(`\n${label}`);
    }
    console.log(JSON.stringify(data, null, 2));
  }
}

/**
 * API client using axios with SDK types
 */
async function callAPI(messages: MessageParam[]): Promise<AnthropicMessage> {
  const response = await apiClient.post<AnthropicMessage>("/messages", {
    model: MODEL,
    max_tokens: 1024,
    system:
      "Bạn là agent phân tích repo. Dùng tool để kiểm chứng trước khi trả lời.",
    tools: TOOLS,
    messages,
  });

  return response.data;
}

/**
 * Agent loop với termination conditions
 */
async function agent(task: string): Promise<string> {
  const messages: MessageParam[] = [{ role: "user", content: task }]; // session state

  for (let turn = 0; turn < MAX_TURNS; turn++) {
    await printJson(messages, `=== Turn ${turn} - Messages ===`);

    const response = await callAPI(messages);

    console.log(
      `\n=== Turn ${turn} - Response ===\nstop=${response.stop_reason} | in=${response.usage.input_tokens} | out=${response.usage.output_tokens}`
    );
    await printJson(response.content);

    messages.push({
      role: "assistant",
      content: response.content,
    });

    if (response.stop_reason !== "tool_use") {
      // natural stop
      return response.content
        .filter((block): block is TextBlock => block.type === "text")
        .map((block) => block.text)
        .join("");
    }

    // Tool execution phase
    const toolResults: Array<{
      type: "tool_result";
      tool_use_id: string;
      content: string;
    }> = [];
    for (const block of response.content) {
      if (block.type === "tool_use") {
        const toolUseBlock = block as ToolUseBlock;
        console.log(
          `  tool_use ${toolUseBlock.name} ${JSON.stringify(toolUseBlock.input)}`
        );

        const result = await runShell(
          (toolUseBlock.input as { command: string }).command
        );

        toolResults.push({
          type: "tool_result",
          tool_use_id: toolUseBlock.id,
          content: result,
        });
      }
    }

    messages.push({
      role: "user",
      content: toolResults,
    }); // observe
  }

  return "STOPPED: max turns reached"; // budget stop
}

// Main execution
if (import.meta.url === `file://${process.argv[1]}`) {
  agent(
    "Repo này có bao nhiêu file Markdown và file nào dài nhất, ko kiểm tra node_modules?"
  )
    .then((result) => {
      console.log("\n=== Final Answer ===");
      console.log(result);
    })
    .catch((error) => {
      console.error("Error:", error);
      process.exit(1);
    });

  // Alternative task:
  // agent("Liệt kê các file trong thư mục này, sau đó đếm số dòng của file main.py")
}
