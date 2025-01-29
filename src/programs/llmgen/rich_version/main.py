# src/programs/llmgen/main.py

import typer
from typing import Optional
from pathlib import Path
import sys
from rich.console import Console
from dotenv import load_dotenv

from src.programs.llmgen.rich_version.chat import LLMGenChat, LLMGenConfig

app = typer.Typer(
    help="LLMGen Chat - Advanced LLM-powered chat interface",
    add_completion=False
)

console = Console()


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
            mode=mode,
            model_name=model,
            system_prompt_path=str(system_prompt) if system_prompt else None,
            streaming=streaming
        )

        # Initialize and run chat
        chat = LLMGenChat(config)

        # Load history if specified
        if history_file:
            chat.commands.handle_command(f"/load {history_file}")

        # Start chat loop
        chat.run()
        return 0

    except Exception as e:
        console.print(f"[red]Error starting LLMGen Chat: {str(e)}[/red]")
        return 1


def main():
    """Main entry point for the LLMGen CLI"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
