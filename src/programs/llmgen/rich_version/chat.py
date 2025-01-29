import os
from typing import Optional, List
from rich.console import Console
from loguru import logger
from pydantic import BaseModel

from src.framework.core.engine import ToolEngine
from src.interfaces.cli import ToolCLI
from src.framework.clients import ClientOpenAI
from tools.core.terminal import TerminalOperations
from tools.pwsh import execute_command
from src.programs.llmgen.rich_version.observer import LLMGenObserver
from src.programs.llmgen.rich_version.commands import CommandRegistry
from src.framework.types.events import EngineObserverEventType

# Configure logging
logger.remove()
logger.add("outputs/logs/llmgen.log", rotation="10 MB", level="INFO")
logger.info("Starting LLMGen Chat")

# Constants
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM_PROMPT_PATH = "prompts/core/agents/system.md"


class LLMGenConfig(BaseModel):
    """Configuration model for LLMGen Chat"""
    mode: str
    model_name: str = DEFAULT_MODEL
    system_prompt_path: Optional[str] = DEFAULT_SYSTEM_PROMPT_PATH
    api_key: Optional[str] = None
    streaming: bool = False


class LLMGenChat:
    def __init__(self, config: LLMGenConfig):
        """Initialize LLMGen Chat with configuration"""
        self.config = config
        self.console = Console()
        self.api_key = config.api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and OPENAI_API_KEY not found in environment")

        self.streaming = config.streaming
        self.client = ClientOpenAI.create_openai(self.api_key)
        self.terminal = TerminalOperations(".")

        # Initialize CLI interface
        self.cli = self._setup_cli()

        # Initialize command registry
        self.commands = CommandRegistry(self)

        # Initialize engine with observer
        self.engine = self._setup_engine()
        self.observer = LLMGenObserver(self.cli)
        self.engine.subscribe(self.observer)

    def _setup_cli(self) -> ToolCLI:
        """Set up the CLI interface"""
        menu_text = """
🤖 LLMGen Chat Interface

Available commands:
- /exit: Exit the program
- /clear: Clear chat history
- /help: Show this menu
- /model <name>: Switch to a different model
- /mode <mode>: Change engine mode
- /system <path>: Load new system prompt
- /tools: List available tools
- /history: Show chat history
- /export: Export chat history
- /load: Load chat history

Type your message to begin...
"""
        return ToolCLI(menu_text=menu_text)

    def _setup_engine(self) -> ToolEngine:
        """Set up the tool engine"""
        system_prompt = None

        # Only try to load system prompt if path is provided
        if self.config.system_prompt_path:
            try:
                with open(self.config.system_prompt_path, 'r', encoding='utf-8') as file:
                    system_prompt = file.read()
            except FileNotFoundError:
                logger.warning(f"System prompt file not found at {self.config.system_prompt_path}")
                system_prompt = "You are a helpful assistant that uses available tools."
        else:
            # Use default system prompt when no path provided
            system_prompt = "You are a helpful assistant that uses available tools."

        return ToolEngine(
            client=self.client,
            model_name=self.config.model_name,
            tools=[
                self.terminal.list_directory,
                self.terminal.read_file,
                self.terminal.write_file,
                self.terminal.delete_file,
                self.terminal.create_directory,
                execute_command,
            ],
            mode=self.config.mode,
            system_prompt=system_prompt,
            confirm_function_call=True,
            stream_output=self.streaming
        )

    def run(self):
        """Run the chat interface"""
        try:
            self.cli.print_info("Welcome to LLMGen Chat! Type /help for available commands.")
            count = 1

            while True:
                try:
                    user_input = self.cli.get_input()

                    # Handle commands
                    if user_input.startswith('/'):
                        if self.commands.handle_command(user_input):
                            continue

                    # Process regular message
                    self.cli.add_message(user_input, "You", "blue")
                    count += 1
                    self.cli.redraw()

                    # Execute the request
                    response = self.engine.execute(user_input)
                    self.engine.subject.notify({
                        "type": EngineObserverEventType.STATUS_UPDATE,
                        "message": "done"
                    })
                    if self.engine.streaming:
                        self.cli.print_streamed_message(response)

                    # Process new messages
                    messages = self.engine.store.retrieve()
                    self._process_messages(count, messages)
                    count = len(messages)

                    self.cli.redraw()

                except KeyboardInterrupt:
                    if self.cli.get_input("Do you want to exit? (y/n): ").lower() == 'y':
                        break
                    continue

        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
            self.cli.print_error(f"Fatal error: {str(e)}")
        finally:
            logger.info("Shutting down LLMGen Chat")

    def _process_messages(self, count: int, messages: List[dict]):
        """Process and display messages"""
        for i in range(count, len(messages)):
            msg = messages[i]
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    self.cli.add_message(msg.get("content"), "You", "blue")
                elif msg.get("role") == "assistant":
                    self.cli.add_message(msg.get("content"), "Assistant", "green")
                elif msg.get("role") == "tool":
                    self.cli.add_message(
                        msg.get("content")[:500],
                        msg.get("name", "Tool"),
                        "yellow"
                    )
