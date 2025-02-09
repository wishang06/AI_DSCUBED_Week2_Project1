from typing import Optional, List, Union
from rich.console import Console
from rich.traceback import install
from loguru import logger
from pydantic import BaseModel
from rich.pretty import pprint

from framework.core.engine import ToolEngine, SimpleChatEngine
from interfaces.cli import ToolCLI
from tools.core.terminal import TerminalOperations
from tools.pwsh import execute_command
from programs.llmgen_legacy.observer import LLMGenObserver
from programs.llmgen_legacy.commands import CommandRegistry
from framework.types.events import EngineObserverEventType
from tools.test import weather
from framework.utils.runtime import init_global_runtime
from framework.clients.model_manager import set_model, ModelManager
from framework.types.models import ModelRequestConfig
from framework.types.engine_types import EngineTypeMap, EngineType
from framework.types.clients import ClientType
from framework.types.openrouter_providers import OpenRouterProvider

# Configure rich traceback
install(show_locals=True, width=120, extra_lines=3, theme="monokai", word_wrap=True)

# Configure logging
logger.remove()
logger.add("outputs/logs/llmgen.log", rotation="10 MB", level="INFO")
logger.info("Starting LLMGen Chat")


class LLMGenConfig(BaseModel):
    """Configuration model for LLMGen Chat"""

    model_request_config: ModelRequestConfig
    engine: EngineType = EngineType.SimpleChatEngine
    system_prompt_path: Optional[str] = None
    streaming: bool = False
    tools: bool = False


class LLMGenChat:
    def __init__(self, config: LLMGenConfig):
        """Initialize LLMGen Chat with configuration"""
        # Initialize global runtime for model manager
        init_global_runtime()
        self.config = config
        self.model_request_config = config.model_request_config
        self.console = Console()

        self.streaming = config.streaming
        self.engine_type = config.engine

        # Set up initial model and client
        self.client_manager = ModelManager()
        self.set_model(
            self.model_request_config.model_name,
            self.model_request_config.client,
            self.model_request_config.openrouter_providers,
        )

        # Initialize tools and interface components
        self.terminal = TerminalOperations(".")
        self.cli = self._setup_cli()
        self.commands = CommandRegistry(self)

        # Initialize engine with observer
        self.engine = self._setup_engine(self.engine_type)
        self.observer = LLMGenObserver(self.cli)
        self.engine.subscribe(self.observer)

    def set_model(
        self,
        model_name: str,
        provider: Optional[ClientType] = None,
        openrouter_providers: Optional[List[OpenRouterProvider]] = None,
    ):
        """Update the model configuration"""
        self.client, self.model = set_model(model_name, provider, openrouter_providers)
        # If engine exists, update it with new client and model
        if hasattr(self, "engine"):
            self.engine.change_model(self.model, self.client)

    def _setup_cli(self) -> ToolCLI:
        """Set up the CLI interface"""
        menu_text = """
🤖 LLMGen Chat Interface

Available commands:
- /exit: Exit the program
- /clear: Clear chat history
- /help: Show this menu
- /model <name>: Switch to a different model
- /provider <name>: Switch to a different provider
- /system <path>: Load new system prompt
- /tools: List available tools
- /history: Show chat history
- /export: Export chat history
- /load: Load chat history

Type your message to begin...
"""
        return ToolCLI(menu_text=menu_text)

    def _setup_engine(
        self, engine_type: EngineType
    ) -> Union[ToolEngine, SimpleChatEngine]:
        """Set up the chat engine"""
        system_prompt = None
        if self.config.system_prompt_path:
            try:
                with open(
                    self.config.system_prompt_path, "r", encoding="utf-8"
                ) as file:
                    system_prompt = file.read()
            except FileNotFoundError:
                logger.warning(
                    f"System prompt file not found at {self.config.system_prompt_path}"
                )
                system_prompt = "You are a helpful assistant."

        engine_class = EngineTypeMap[engine_type]

        if self.config.tools:
            return engine_class(
                client=self.client,
                model_name=self.model,
                tools=[
                    self.terminal.list_directory,
                    self.terminal.read_file,
                    self.terminal.write_file,
                    self.terminal.delete_file,
                    self.terminal.create_directory,
                    execute_command,
                    weather,
                ],
                mode="normal",
                system_prompt=system_prompt,
                confirm_function_call=True,
                stream_output=self.streaming,
            )
        else:
            return engine_class(
                client=self.client,
                model=self.model,
                system_prompt=system_prompt,
                stream_output=self.streaming,
            )

    def run(self):
        """Run the chat interface"""
        try:
            self.cli.print_info(
                "Welcome to LLMGen Chat! Type /help for available commands."
            )
            count = 1

            while True:
                try:
                    user_input = self.cli.get_input()

                    # Handle commands
                    if user_input.startswith("/"):
                        if self.commands.handle_command(user_input):
                            continue

                    # Process regular message
                    self.cli.add_message(user_input, "You", "blue")
                    count += 1
                    self.cli.redraw()

                    # Execute the request
                    response = self.engine.execute(user_input)
                    self.engine.subject.notify(
                        {
                            "type": EngineObserverEventType.STATUS_UPDATE,
                            "message": "done",
                        }
                    )

                    # Process new messages
                    messages = self.engine.store.retrieve()
                    self._process_messages(count, messages)
                    count = len(messages)

                    self.cli.redraw()

                except KeyboardInterrupt:
                    if (
                        self.cli.get_input("Do you want to exit? (y/n): ").lower()
                        == "y"
                    ):
                        break
                    continue
                except:
                    # Let rich handle the traceback formatting
                    self.console.print_exception()
                    pprint(self.engine.store.response_log[-1])
                    pprint(self.engine.store.retrieve())
                    self.cli.print_info(
                        "You can continue chatting or type 'exit' to quit."
                    )

        except:
            # Let rich handle the traceback formatting
            self.console.print_exception()
            logger.exception("Fatal error in LLMGen Chat")
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
                    if msg.get("content"):
                        self.cli.add_message(msg.get("content"), "Assistant", "green")
                elif msg.get("role") == "tool":
                    self.cli.add_message(
                        msg.get("content")[:500], msg.get("name", "Tool"), "yellow"
                    )
