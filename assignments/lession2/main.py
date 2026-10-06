# minimal_agent.py — harness tối giản để thấy rõ ranh giới model/harness
import json
import os
import subprocess

from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = os.getenv("ANTHROPIC_API_URL")
MODEL = os.getenv("ANTHROPIC_MODEL", "")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
if not API_URL:
    raise ValueError("ANTHROPIC_API_URL not found in environment variables")
if not MODEL:
    raise ValueError("ANTHROPIC_MODEL not found in environment variables")

client = Anthropic(api_key=API_KEY, base_url=API_URL)
MAX_TURNS = 10  # budget stop

TOOLS = [
    {
        "name": "run_shell",
        "description": "Chạy một lệnh shell read-only trong thư mục làm việc. Trả về stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    }
]

ALLOWED_PREFIXES = ("ls", "cat", "grep", "wc", "head", "find")  # guardrail thô sơ


def run_shell(command: str) -> str:
    """Tool execution với guardrails và error handling"""
    if not command.startswith(ALLOWED_PREFIXES):
        return "ERROR: command not allowed"  # tool result handling: lỗi có ngữ nghĩa
    try:
        out = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=10
        )
        return (out.stdout + out.stderr)[:4000]  # cắt ngắn để bảo vệ context
    except subprocess.TimeoutExpired:
        return "ERROR: command timeout after 10s"
    except Exception as e:
        return f"ERROR: {str(e)}"


def print_json(data, label: str = ""):
    """Print JSON với jq nếu available, fallback về json.dumps"""
    json_str = json.dumps(data, ensure_ascii=False)
    try:
        # Try using jq for pretty formatting with color
        result = subprocess.run(
            ["jq", "-C", "."],  # -C for color output
            input=json_str,
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            if label:
                print(f"\n{label}")
            print(result.stdout)
        else:
            # Fallback to Python json
            if label:
                print(f"\n{label}")
            print(json.dumps(data, indent=2, ensure_ascii=False))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        # jq not available, use Python json
        if label:
            print(f"\n{label}")
        print(json.dumps(data, indent=2, ensure_ascii=False))


def agent(task: str) -> str:
    """Agent loop với termination conditions"""
    messages = [{"role": "user", "content": task}]  # session state
    for turn in range(MAX_TURNS):
        # Serialize messages safely
        serializable_messages = []
        for msg in messages:
            if msg["role"] == "assistant":
                serializable_messages.append({
                    "role": msg["role"],
                    "content": [block.model_dump() for block in msg["content"]]
                })
            else:
                serializable_messages.append(msg)
        print_json(serializable_messages, f"=== Turn {turn} - Messages ===")

        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system="Bạn là agent phân tích repo. Dùng tool để kiểm chứng trước khi trả lời.",
            tools=TOOLS,
            messages=messages,
        )

        print(
            f"\n=== Turn {turn} - Response ===\nstop={resp.stop_reason} | in={resp.usage.input_tokens} | out={resp.usage.output_tokens}"
        )
        print_json([block.model_dump() for block in resp.content])
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":  # natural stop
            return "".join(b.text for b in resp.content if b.type == "text")

        # Tool execution phase
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  tool_use {block.name} {json.dumps(block.input)}")
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": run_shell(**block.input),
                    }
                )
        messages.append({"role": "user", "content": results})  # observe

    return "STOPPED: max turns reached"  # budget stop


if __name__ == "__main__":
    print(
        agent(
            "Repo này có bao nhiêu file Markdown và file nào dài nhất, ko kiểm tra .venv?"
        )
    )
    # print(
    # agent("Liệt kê các file trong thư mục này, sau đó đếm số dòng của file main.py")
    # )
