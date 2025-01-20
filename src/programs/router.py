import typer
from pathlib import Path
import importlib.util
import sys
from typing import Optional, List
from enum import Enum

app = typer.Typer()


class Program(str, Enum):
    FUNCTION_STUDIO = "function_studio"
    CLI_FULL = "cli_full"


def import_module_from_path(path: Path):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


@app.callback()
def callback():
    """
    LLMgine CLI - Run various LLM-powered programs
    """
    pass


@app.command()
def function_studio(
        config_file: Path = typer.Argument(..., help="Path to studio test configuration file"),
        args: Optional[List[str]] = typer.Argument(None, help="Additional arguments")
):
    """Run function studio with a test configuration file"""
    try:
        base_path = Path(__file__).parent

        if not config_file.is_absolute():
            # Try to resolve relative to function_studio/tests first
            test_path = base_path / "function_studio" / "tests" / config_file
            if not test_path.exists():
                # Fall back to the provided path
                test_path = config_file
        else:
            test_path = config_file

        if not test_path.exists():
            raise typer.BadParameter(f"Config file not found: {test_path}")

        # Import the program module
        program_path = base_path / "function_studio" / "function_studio.py"
        program_module = import_module_from_path(program_path)

        # Run the program
        program_module.main(test_path)

    except Exception as e:
        typer.echo(f"Error running function studio: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def function_chat(
        mode: str = typer.Argument("normal", help="Engine mode (normal, minimal, chain, linear_chain)"),
        system_prompt: str = typer.Argument(">>>", help="System prompt")
):
    """Run the full CLI interface"""
    try:
        all_args = [mode]
        if args:
            all_args.extend(args)

        program_path = Path(__file__).parent / "function_chat.py"
        program_module = import_module_from_path(program_path)
        program_module.main(args=all_args)
    except Exception as e:
        typer.echo(f"Error running full CLI: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
