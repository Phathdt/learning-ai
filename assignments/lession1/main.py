import os
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    # Get API key, endpoint, and model from environment variables
    api_key = os.getenv("ANTHROPIC_API_KEY")
    api_url = os.getenv("ANTHROPIC_API_URL")
    model = os.getenv("ANTHROPIC_MODEL")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

    if not api_url:
        raise ValueError("ANTHROPIC_API_URL not found in environment variables")

    if not model:
        raise ValueError("ANTHROPIC_MODEL not found in environment variables")

    # Initialize Anthropic client
    client = Anthropic(api_key=api_key, base_url=api_url)

    # Create a message
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello! Can you introduce yourself?"}],
    )

    # Print the response
    print("Response from Claude:")
    print(message.content[0].text)


if __name__ == "__main__":
    main()
