import typer
from typing import Optional
from pathlib import Path
import sys
from rich.console import Console
from rich.traceback import install
from dotenv import load_dotenv

from src.framework.types.models import ModelRequestConfig
from src.programs.llmgen.chat import LLMGenChat, LLMGenConfig
from src.framework.clients.model_manager import set_model
from src.framework.types.engine_types import EngineType, EngineTypeMap

# Install rich traceback handler with extended configuration
install(show_locals=True, width=120, extra_lines=3, theme="monokai", word_wrap=True)

app = typer.Typer(
    help="LLMGen Chat - Advanced LLM-powered chat interface",
    add_completion=False
)

console = Console()


@app.command()
def chat(
        engine: str = typer.Option(
            "SimpleChatEngine",
            "--engine", "-e",
            help="Engine (SimpleChatEngine, ToolEngine)"
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
            exists=False,  # Changed to False to avoid validation error when not provided
            file_okay=True,
            dir_okay=False,
        ),
        history_file: Optional[Path] = typer.Option(
            None,
            "--history", "-h",
            help="Path to load chat history from"
        ),
        streaming: Optional[bool] = typer.Option(
            False,
            help="Enable streaming mode"
        )
):
    """Start the LLMGen chat interface"""
    try:
        # Load environment variables
        load_dotenv()

        # Create configuration
        config = LLMGenConfig(
            model_request_config=ModelRequestConfig(
                model_name=model
            ),
            engine = EngineTypeMap[engine],
            system_prompt_path=system_prompt,
            streaming=streaming,
            tools=False
        )

        # Initialize and run chat
        chat = LLMGenChat(config)

        # Load history if specified
        if history_file:
            chat.commands.handle_command(f"/load {history_file}")

        # Start chat loop
        chat.run()
        return 0

    except Exception:
        # Let rich.traceback handle the exception formatting
        console.print_exception()
        return 1


def main():
    """Main entry point for the LLMGen CLI"""
    try:
        app()
    except Exception:
        # Let rich.traceback handle the exception formatting
        console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
