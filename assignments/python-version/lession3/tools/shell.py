"""
Shell tool - Execute read-only shell commands với guardrails
"""
import subprocess

# Allowed command prefixes (read-only operations)
ALLOWED_PREFIXES = ("ls", "cat", "grep", "wc", "head", "find", "pwd")

# Patterns to exclude from results
EXCLUDE_PATTERNS = [".venv", "__pycache__", ".git", "node_modules", ".pyc"]


def filter_output(output: str) -> str:
    """
    Filter output để loại bỏ các dòng chứa patterns không mong muốn

    Args:
        output: Raw output từ command

    Returns:
        Filtered output
    """
    lines = output.split('\n')
    filtered_lines = []

    for line in lines:
        # Bỏ qua dòng có chứa bất kỳ exclude pattern nào
        if not any(pattern in line for pattern in EXCLUDE_PATTERNS):
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)


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
        # Auto-add exclude patterns to find commands
        modified_command = command
        if command.startswith("find") and "-name" in command:
            # Build exclude clause for find
            exclude_parts = []
            for pattern in EXCLUDE_PATTERNS:
                exclude_parts.append(f"-path '*{pattern}*' -prune -o")

            # Insert after 'find .' and before other conditions
            if "find ." in command:
                parts = command.split("find .", 1)
                if len(parts) == 2:
                    # find . [exclude clauses] [original conditions] -print
                    exclude_clause = " ".join(exclude_parts)
                    modified_command = f"find . {exclude_clause} {parts[1].strip()} -print"

        result = subprocess.run(
            modified_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        raw_output = result.stdout + result.stderr

        # Filter output
        filtered_output = filter_output(raw_output)

        # Truncate if too long
        output = filtered_output[:4000]

        return output if output.strip() else "Command executed successfully (no output)"

    except subprocess.TimeoutExpired:
        return "ERROR: command timeout after 10s"
    except Exception as e:
        return f"ERROR: {str(e)}"
