import os
import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv
import typer
from rich.console import Console

from src.framework.core.engine import ToolEngine
from src.framework.clients import ClientOpenAI
from tools.core.terminal import TerminalOperations
from tools.pwsh import execute_command
from src.framework.core.observer import Observer
from src.programs.llmgen.chat import ChatInterface, Message, MessageType
from src.programs.llmgen.commands import CommandHandler

# Configure logging
logger.remove()
logger.add("outputs/logs/llmgen.log", rotation="10 MB", level="INFO")
logger.info("Starting LLMGen Chat")

# Constants
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM_PROMPT_PATH = "prompts/core/agents/system.md"


class LLMGenObserver(Observer):
    """Observer for handling LLM engine events"""

    def __init__(self, chat_interface: ChatInterface):
        self.chat = chat_interface
        self.current_stream = None

    def update(self, event: Dict[str, Any]):
        """Handle various engine events"""
        if event["type"] == "response":
            if not self.current_stream:
                self.chat.display_message(
                    Message(
                        content=event["content"],
                        type=MessageType.ASSISTANT
                    )
                )
        elif event["type"] == "function_call":
            self.chat.display_message(
                Message(
                    content=str(event["parameters"]),
                    type=MessageType.TOOL_CALL,
                    metadata={"name": event["name"]}
                )
            )
        elif event["type"] == "function_result":
            self.chat.display_message(
                Message(
                    content=event["content"]["content"],
                    type=MessageType.TOOL_RESULT,
                    metadata={"name": event["name"]}
                )
            )

    def get_input(self, event: Any) -> str:
        """Handle input requests"""
        return self.chat.get_input(event["message"])


class LLMGenChat:
    """Main chat application class"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()

        # Initialize API client
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and OPENAI_API_KEY not found in environment")

        self.client = ClientOpenAI.create_openai(self.api_key)
        self.terminal = TerminalOperations(".")

        # Initialize interface and command handler
        self.chat_interface = ChatInterface()
        self.commands = CommandHandler(self.chat_interface, self)

        # Initialize engine with observer
        self.engine = self._setup_engine()
        self.engine.subscribe(LLMGenObserver(self.chat_interface))

    def _setup_engine(self) -> ToolEngine:
        """Set up the LLM engine"""
        system_prompt = None

        # Try to load system prompt from file if specified
        if self.config.get("system_prompt_path"):
            try:
                with open(self.config["system_prompt_path"], 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except Exception as e:
                logger.warning(f"Error loading system prompt: {e}")
                system_prompt = "You are a helpful assistant that uses available tools."

        return ToolEngine(
            client=self.client,
            model_name=self.config.get("model_name", DEFAULT_MODEL),
            tools=[
                self.terminal.list_directory,
                self.terminal.read_file,
                self.terminal.write_file,
                self.terminal.delete_file,
                self.terminal.create_directory,
                execute_command,
            ],
            mode=self.config.get("mode", "normal"),
            system_prompt=system_prompt
        )

    async def run(self):
        """Run the chat interface"""
        try:
            # Show welcome message
            self.chat_interface.display_message(
                Message(
                    content="Welcome to LLMGen Chat! Type /help for available commands.",
                    type=MessageType.SYSTEM
                )
            )

            while True:
                try:
                    # Get user input
                    user_input = await self.chat_interface.get_input()

                    # Handle exit command
                    if user_input.lower() in ["exit", "quit"]:
                        self.chat_interface.display_message(
                            Message(
                                content="Goodbye! 👋",
                                type=MessageType.SYSTEM
                            )
                        )
                        break

                    # Handle commands
                    if user_input.startswith('/'):
                        if self.commands.handle_command(user_input):
                            continue

                    # Display user message
                    self.chat_interface.display_message(
                        Message(
                            content=user_input,
                            type=MessageType.USER
                        )
                    )

                    # Process with engine
                    response = self.engine.create_streaming_completion(
                        self.engine.model_name,
                        self.engine.store.retrieve()
                    )

                    # Stream response
                    accumulated_response = await self.chat_interface.stream_response(response)

                    # Store final response
                    self.engine.store.store_string(accumulated_response, "assistant")

                except KeyboardInterrupt:
                    confirm = await self.chat_interface.get_input(
                        "Do you want to exit? (y/n): "
                    )
                    if confirm.lower() == 'y':
                        break
                    continue
                except Exception as e:
                    logger.error(f"Error in chat loop: {str(e)}")
                    self.chat_interface.display_error(f"Error: {str(e)}")

        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            self.chat_interface.display_error(f"Fatal error: {str(e)}")
        finally:
            logger.info("Shutting down LLMGen Chat")


app = typer.Typer(
    help="LLMGen Chat - Advanced LLM-powered chat interface",
    add_completion=False
)


@app.command()
def chat(
        mode: str = typer.Option(
            "normal",
            "--mode", "-m",
            help="Engine mode (normal, minimal, chain, linear_chain)"
        ),
        model: str = typer.Option(
            "gpt-4o-mini",
            "--model",
            help="Model to use for chat"
        ),
        system_prompt: Optional[Path] = typer.Option(
            None,
            "--system-prompt", "-s",
            help="Path to system prompt file",
            exists=False,
            file_okay=True,
            dir_okay=False,
        ),
        history_file: Optional[Path] = typer.Option(
            None,
            "--history", "-h",
            help="Path to load chat history from"
        )
):
    """Start the LLMGen chat interface"""
    try:
        # Load environment variables
        load_dotenv()

        # Create configuration
        config = {
            "mode": mode,
            "model_name": model,
            "system_prompt_path": str(system_prompt) if system_prompt else None
        }

        # Initialize and run chat
        chat = LLMGenChat(config)

        # Load history if specified
        if history_file:
            chat.commands.handle_command(f"/load {history_file}")

        # Run chat loop
        asyncio.run(chat.run())
        return 0

    except Exception as e:
        Console().print(f"[red]Error starting LLMGen Chat: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    app()
