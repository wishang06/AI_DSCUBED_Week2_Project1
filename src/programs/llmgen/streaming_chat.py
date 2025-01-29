# src/programs/llmgen/rich_version/streaming_chat.py

import os
import asyncio
import prompt_toolkit
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import PromptSession
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.text import Text
from rich import box
from typing import Optional, List, Dict, Any, Union
from loguru import logger

from src.framework.core.engine import ToolEngine
from src.framework.clients.openai_client import ClientOpenAI
from src.framework.core.observer import Observer
from src.interfaces.cli.cli import ToolCLI  # Optional, if you want to reuse or adapt
from src.programs.llmgen.commands_streaming import StreamingCommandRegistry
from src.framework.tool_calling.tool_calling import create_tools_schema

from tools.core.terminal import TerminalOperations
from tools.pwsh import execute_command

# If you have other tools, add them to the list below
DEFAULT_TOOLS = [
    TerminalOperations.list_directory,
    TerminalOperations.read_file,
    TerminalOperations.write_file,
    TerminalOperations.delete_file,
    TerminalOperations.create_directory,
    execute_command
]

logger.remove()
logger.add("outputs/logs/streaming_chat.log", level="INFO", rotation="10 MB")
logger.info("Starting Streaming Chat")

DEFAULT_SYSTEM_PROMPT = """\
You are an assistant that can stream responses. You also have access to tools.
"""


class StreamingObserver(Observer):
    """
    Observes the LLM streaming responses and updates the console in real-time.
    """

    def __init__(self, console: Console):
        self.console = console
        self.partial_content = ""
        self.is_streaming = False

    def update(self, event: Dict[str, Any]):
        """React to events from the engine or tool manager."""
        etype = event.get("type")
        if etype == "function_call":
            # Show tool call info
            fn_name = event["name"]
            params = event["parameters"]
            self.console.print(
                Panel(
                    f"[bold]Tool Call:[/bold] {fn_name}\n[bold]Params:[/bold] {params}",
                    title="Tool Call",
                    style="yellow",
                    box=box.ROUNDED,
                )
            )

        elif etype == "function_result":
            # Show tool call result
            result_content = event["content"]["content"]
            fn_name = event["name"]
            self.console.print(
                Panel(
                    f"[bold]Result ({fn_name}):[/bold]\n{result_content[:600]}",
                    title="Tool Result",
                    style="green",
                    box=box.ROUNDED,
                )
            )

        elif etype == "status_update":
            if event["message"] == "done":
                # Possibly finalize any streaming states
                pass
            else:
                self.console.log(f"[status_update] {event['message']}")

        else:
            self.console.log(f"[observer] Unhandled event: {event}")

    def get_input(self, event: Any) -> Union[str, bool]:
        """
        If engine requests a confirm or input.
        This is synchronous for simplicity.
        """
        if event["type"] == "confirm":
            prompt = f"{event['message']} (y/n)? "
            response = input(prompt).lower().strip()
            return response in ["y", "yes"]
        return input(f"{event['message']}: ")


class StreamingChat:
    """
    A streaming chat interface that uses prompt_toolkit for user input
    and Rich for streaming output. Integrates with ToolEngine to
    handle function calls.
    """

    def __init__(
            self,
            mode: str = "normal",
            model_name: str = "gpt-4",
            system_prompt: str = DEFAULT_SYSTEM_PROMPT,
            api_key: Optional[str] = None,
            tools: Optional[List[callable]] = None
    ):
        self.console = Console()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set or provided.")
        self.client = ClientOpenAI.create_openai(self.api_key)
        self.tools = tools or DEFAULT_TOOLS
        self.mode = mode
        self.model_name = model_name
        self.system_prompt = system_prompt

        # Build engine
        self.engine = ToolEngine(
            client=self.client,
            model_name=self.model_name,
            tools=self.tools,
            mode=self.mode,
            system_prompt=self.system_prompt,
        )
        # Observers
        self.observer = StreamingObserver(self.console)
        self.engine.subscribe(self.observer)

        # Command registry
        self.command_registry = StreamingCommandRegistry(self)

        # Chat history count index
        self.history_count = 0

    def print_intro(self):
        """Show an intro message in Rich."""
        self.console.clear()
        intro_text = (
            f"[bold magenta]Welcome to Streaming Chat![/bold magenta]\n"
            f"Model: {self.model_name}, Mode: {self.mode}\n"
            f"Type /help for commands. Ctrl+C to quit.\n"
        )
        self.console.print(
            Panel(
                Text(intro_text, justify="center"),
                box=box.HEAVY,
                style="blue",
            )
        )

    async def run_chat(self):
        """
        Main loop for streaming chat. Uses prompt_toolkit for user input
        while still allowing asynchronous streaming output if needed.
        """
        self.print_intro()
        session = PromptSession()

        while True:
            try:
                with patch_stdout():
                    user_input = await session.prompt_async("> ")

                # Check if it's a command
                if user_input.strip().startswith("/"):
                    handled = self.command_registry.handle_command(user_input)
                    if handled:
                        continue
                    else:
                        self.console.print(f"[red]Unknown command:[/red] {user_input}")
                        continue

                # Regular input, process
                self.display_user_message(user_input)
                self.process_message(user_input)

            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[bold red]Exiting...[/bold red]")
                break

    def display_user_message(self, message: str):
        """Display the user's message in a Rich panel."""
        self.console.print(
            Panel(
                Markdown(message),
                title="You",
                style="green",
                box=box.ROUNDED
            )
        )

    def display_assistant_message(self, message: str):
        """Display the assistant's final message in a Rich panel."""
        self.console.print(
            Panel(
                Markdown(message),
                title="Assistant",
                style="cyan",
                box=box.ROUNDED
            )
        )

    def process_message(self, message: str):
        """
        For now, we’ll do a single turn (non-streaming) with the underlying
        create_tool_completion or create_completion. If you want actual
        partial-token streaming from OpenAI, you'll adapt the engine logic.
        """
        response = self.engine.execute(message)
        # The `response` is typically a `ResponseWrapperOpenAI` with .content
        final_content = response.content
        if final_content:
            self.display_assistant_message(final_content)

        # We'll also mark "done"
        self.engine.subject.notify({"type": "status_update", "message": "done"})
