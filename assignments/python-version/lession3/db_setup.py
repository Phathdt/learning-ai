"""
Database setup và checkpointer initialization
"""

import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

# Load environment variables
load_dotenv()


def get_db_connection_string() -> str:
    """Build PostgreSQL connection string từ env vars"""
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "agentdb")
    db_user = os.getenv("DB_USER", "agent")
    db_password = os.getenv("DB_PASSWORD", "agent123")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def create_checkpointer() -> PostgresSaver:
    """
    Create PostgreSQL checkpointer instance

    Returns:
        PostgresSaver instance connected to database
    """
    conn_string = get_db_connection_string()

    # Create persistent connection
    connection = psycopg.connect(
        conn_string,
        autocommit=True,
        prepare_threshold=0
    )

    # Create checkpointer
    checkpointer = PostgresSaver(connection)

    # Setup tables if not exist
    checkpointer.setup()

    return checkpointer


def get_checkpointer() -> PostgresSaver:
    """
    Get singleton checkpointer instance

    Returns:
        Cached PostgresSaver instance
    """
    if not hasattr(get_checkpointer, "_instance"):
        get_checkpointer._instance = create_checkpointer()
    return get_checkpointer._instance


if __name__ == "__main__":
    """Test checkpointer setup"""
    print("Setting up PostgreSQL checkpointer...")
    print(f"Connection: {get_db_connection_string()}")

    checkpointer = create_checkpointer()
    print("✓ Checkpointer setup successfully!")
    print("✓ Tables created in database")
    print(f"✓ Type: {type(checkpointer)}")
