import typer
from pathlib import Path
import importlib.util
import sys
from typing import Optional, List
from enum import Enum
from rich.console import Console

app = typer.Typer(
    help="LLMgine CLI - Run various LLM-powered programs",
    add_completion=False
)

console = Console()


class Program(str, Enum):
    FUNCTION_STUDIO = "function-studio"
    FUNCTION_CHAT = "function-chat"
    LLMGEN = "llmgen"


def import_module_from_path(path: Path):
    """Import a module from a file path"""
    try:
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module spec for {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        raise ImportError(f"Error importing module {path}: {str(e)}")


@app.command()
def function_studio(
        config_file: Path = typer.Argument(
            ...,
            help="Path to studio test configuration file"
        )
):
    """Run Function Studio with a test configuration file"""
    try:
        base_path = Path(__file__).parent

        # Try to resolve relative to function_studio/tests first
        if not config_file.is_absolute():
            test_path = base_path / "function_studio" / "tests" / config_file
            if not test_path.exists():
                test_path = config_file
        else:
            test_path = config_file

        if not test_path.exists():
            raise typer.BadParameter(f"Config file not found: {test_path}")

        # Import and run the program module
        program_path = base_path / "function_studio" / "function_studio.py"
        program_module = import_module_from_path(program_path)

        return program_module.main(test_path)

    except Exception as e:
        console.print(f"[red]Error running Function Studio: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def function_chat(
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
            exists=True,
            file_okay=True,
            dir_okay=False,
        )
):
    """Run the Function Chat interface"""
    try:
        # Import the function chat module
        program_path = Path(__file__).parent / "function_chat.py"
        program_module = import_module_from_path(program_path)

        # Run the chat program
        return program_module.main(
            mode=mode,
            model_name=model,
        )

    except Exception as e:
        console.print(f"[red]Error running Function Chat: {str(e)}[/red]")
        raise typer.Exit(1)


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
        )
):
    """Run LLMGen rich implementation"""
    try:
        # Import the LLMGen rich implementation module
        program_path = Path(__file__).parent / "llmgen" / "rich_version" / "main.py"
        program_module = import_module_from_path(program_path)

        # Run the chat program with provided arguments
        sys.argv = [sys.argv[0]]  # Reset sys.argv to avoid typer argument conflicts
        return program_module.main()

    except Exception as e:
        console.print(f"[red]Error running LLMGen: {str(e)}[/red]")
        raise typer.Exit(1)


@app.callback()
def callback():
    """
    LLMgine CLI - Run various LLM-powered programs
    """
    pass


def main():
    """Entry point for the router CLI"""
    try:
        app()
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
