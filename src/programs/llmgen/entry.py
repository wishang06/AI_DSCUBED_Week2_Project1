from pathlib import Path
import os
from dotenv import load_dotenv
import src.programs.llmgen.code as code
import asyncio

# Load environment variables
load_dotenv()

# Create chat instance
chat = code.create_streaming_chat(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="gpt-4o-mini",
    system_prompt="You are a helpful assistant."
)

# Run the chat
asyncio.run(chat.run())
