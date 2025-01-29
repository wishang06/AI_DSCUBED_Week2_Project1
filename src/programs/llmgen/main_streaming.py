# src/programs/llmgen/rich_version/main_streaming.py

import typer
import asyncio
from typing import Optional
from rich.console import Console
from dotenv import load_dotenv
from pathlib import Path
import os

from src.programs.llmgen.streaming_chat import StreamingChat

app = typer.Typer(help="Streaming LLMGen Chat CLI")


@app.command()
def chat(
        mode: str = typer.Option(
            "normal", help="Engine mode (normal, minimal, chain, linear_chain)"
        ),
        model: str = typer.Option(
            "gpt-4o-mini", help="Model to use"
        ),
        system_prompt_file: Optional[Path] = typer.Option(
            None,
            "--system-prompt", "-s",
            help="System prompt file path"
        )
):
    """
    Start a streaming chat with LLM + tools.
    """
    load_dotenv()
    console = Console()

    system_prompt = None
    if system_prompt_file:
        if not system_prompt_file.exists():
            console.print(f"[red]System prompt file not found: {system_prompt_file}[/red]")
            raise typer.Exit(1)
        try:
            system_prompt = system_prompt_file.read_text(encoding="utf-8")
        except Exception as e:
            console.print(f"[red]Error reading system prompt: {e}[/red]")
            raise typer.Exit(1)

    # Initialize chat
    try:
        chat_app = StreamingChat(
            mode=mode,
            model_name=model,
            system_prompt=system_prompt or "",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # Run async loop for the chat
        asyncio.run(chat_app.run_chat())

    except Exception as e:
        console.print(f"[red]Failed to start streaming chat: {e}[/red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
