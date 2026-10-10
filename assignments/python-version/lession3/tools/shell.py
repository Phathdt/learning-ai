"""
Shell tool - Execute read-only shell commands với guardrails
"""
import subprocess

# Allowed command prefixes (read-only operations)
ALLOWED_PREFIXES = ("ls", "cat", "grep", "wc", "head", "find", "pwd")


def run_shell_tool(command: str) -> str:
    """
    Chạy lệnh shell read-only với guardrails

    Args:
        command: Lệnh shell cần chạy

    Returns:
        Output của lệnh hoặc error message
    """
    if not command.startswith(ALLOWED_PREFIXES):
        return f"ERROR: command not allowed. Only these prefixes are allowed: {ALLOWED_PREFIXES}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = (result.stdout + result.stderr)[:4000]
        return output if output else "Command executed successfully (no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: command timeout after 10s"
    except Exception as e:
        return f"ERROR: {str(e)}"
