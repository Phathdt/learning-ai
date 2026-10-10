"""
Shell tool - Execute read-only shell commands với guardrails
"""
import subprocess
from tools.logger import setup_logger, log_tool_call, log_tool_result

# Setup logger
logger = setup_logger("shell_tool")

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
    log_tool_call(logger, "run_shell_tool", command=command)

    if not command.startswith(ALLOWED_PREFIXES):
        error_msg = f"ERROR: command not allowed. Only these prefixes are allowed: {ALLOWED_PREFIXES}"
        log_tool_result(logger, "run_shell_tool", success=False, error=error_msg)
        return error_msg

    try:
        # Auto-add exclude patterns to find commands
        modified_command = command
        if command.startswith("find") and "-name" in command:
            logger.debug("Adding exclude patterns to find command")
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

        logger.debug(f"Executing: {modified_command}")
        result = subprocess.run(
            modified_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        raw_output = result.stdout + result.stderr
        logger.debug(f"Raw output length: {len(raw_output)} chars")

        # Filter output
        filtered_output = filter_output(raw_output)
        logger.debug(f"Filtered output length: {len(filtered_output)} chars")

        # Truncate if too long
        output = filtered_output[:4000]
        if len(filtered_output) > 4000:
            logger.warning(f"Output truncated from {len(filtered_output)} to 4000 chars")

        result_msg = output if output.strip() else "Command executed successfully (no output)"
        log_tool_result(logger, "run_shell_tool", success=True, result=result_msg)
        return result_msg

    except subprocess.TimeoutExpired:
        error_msg = "ERROR: command timeout after 10s"
        log_tool_result(logger, "run_shell_tool", success=False, error=error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        log_tool_result(logger, "run_shell_tool", success=False, error=error_msg)
        return error_msg
