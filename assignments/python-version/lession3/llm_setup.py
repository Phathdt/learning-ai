"""
LLM setup và configuration
"""
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("ANTHROPIC_API_KEY")
API_URL = os.getenv("ANTHROPIC_API_URL")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

if not API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")


def create_llm():
    """
    Tạo LLM instance cơ bản (không bind tools)

    Returns:
        ChatAnthropic instance
    """
    return ChatAnthropic(
        model_name=MODEL,
        api_key=API_KEY,
        base_url=API_URL,
        timeout=60.0,
        stop=None
    )


def get_llm_with_tools(tools: list):
    """
    Tạo LLM instance với tools binding

    Args:
        tools: List các tool functions

    Returns:
        ChatAnthropic instance đã bind tools
    """
    llm = create_llm()
    return llm.bind_tools(tools)
