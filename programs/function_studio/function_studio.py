import json
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, List, Dict, Union, Callable

import dotenv
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.syntax import Syntax
from rich.text import Text
from rich.table import Table
from loguru import logger
from rich.pretty import Pretty
import textwrap

from framework.clients import ClientOpenAI
from framework.core.engine import ToolEngine
from framework.utils import CLIStatusCallback
from interfaces.cli import ToolCLI
from framework.core.observer import Observer
from interfaces.cli.observer import CLIObserver
from tools.core.terminal import TerminalOperations

dotenv.load_dotenv()

console = Console()
logger.remove()


@dataclass
class ToolImport:
    """Configuration for importing a tool"""
    module_path: str
    names: List[str]
    class_name: Optional[str] = None
    class_args: Optional[Dict[str, Any]] = None
    relative_import: bool = True


@dataclass
class ContextFile:
    """Configuration for a context file"""
    path: str
    description: Optional[str] = None


class FunctionStudioObserver(Observer):
    """Enhanced Function Studio Observer with cumulative test results display and CSV export"""

    def __init__(self, config_path: str = None):
        self.cli = Console()
        self.spinner = None
        self.live = None
        self.current_test_number = 0
        self.all_results = []  # Store all test results
        self.current_test_results = []  # Store current test results
        self.config_path = config_path
        self.all_tests_complete = False

    def create_csv_filename(self) -> Path:
        """Create a filename for the CSV export based on config name and timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if self.config_path:
            config_name = Path(self.config_path).stem
        else:
            config_name = "function_studio"

        # Create results directory relative to current working directory
        results_dir = Path("src/programs/function_studio/results")
        results_dir.mkdir(parents=True, exist_ok=True)

        return results_dir / f"{config_name}_{timestamp}.csv"

    def export_to_csv(self):
        """Export all results to a CSV file"""
        import csv
        # Only export if we have results and all tests are complete
        if not self.all_results or not self.all_tests_complete:
            return

        filename = self.create_csv_filename()

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['Test Number', 'Function', 'Parameters', 'Result'])

            # Write results
            for test_num, results in enumerate(self.all_results, 1):
                for func_name, params, result in results:
                    writer.writerow([test_num, func_name, params, result])

        self.cli.print(f"\n💾 Results saved to: {filename}\n", style="bold green")

    def create_cumulative_table(self) -> Table:
        """Create a table with all test results"""
        table = Table(
            title="📊 Function Studio Test Results",
            show_header=True,
            header_style="bold magenta",
            title_style="bold blue",
            border_style="blue"
        )

        # Add columns
        table.add_column("Test #", style="bold cyan", justify="center")
        table.add_column("Function", style="cyan", no_wrap=True)
        table.add_column("Parameters", style="green")
        table.add_column("Result", style="yellow", overflow="fold")

        # Add all historical results
        for test_num, results in enumerate(self.all_results, 1):
            # Add a separator row between tests if not the first test
            if test_num > 1:
                table.add_row(
                    "―" * 4,
                    "―" * 20,
                    "―" * 30,
                    "―" * 40,
                    style="dim blue"
                )

            # Add results for this test
            for func_name, params, result in results:
                table.add_row(
                    str(test_num),
                    func_name,
                    params,
                    result
                )

        return table

    def format_parameters(self, params: Dict) -> str:
        """Format parameters for display in table"""
        try:
            if not params:
                return "-"
            return "\n".join(f"{k}: {v}" for k, v in params.items())
        except Exception:
            return str(params)


    def format_result(self, result: Any) -> str:
        """Format result for display in table with improved pretty printing"""
        try:
            from pprint import pformat

            if isinstance(result, (dict, list)):
                # Use pformat with indent=2 for better table readability
                return pformat(result, indent=2, width=60)
            elif isinstance(result, str):
                try:
                    # Try to parse string as JSON
                    parsed = json.loads(result)
                    return pformat(parsed, indent=2, width=60)
                except json.JSONDecodeError:
                    return result
            else:
                return pformat(result, indent=2, width=60)
        except Exception as e:
            return f"Error formatting result: {str(e)}"

    def start_loading(self, message: str):
        """Start loading spinner"""
        self.spinner = Spinner("dots", text=Text(f"🔄 {message}", style="yellow"))
        if self.live is None:
            self.live = Live(
                self.spinner,
                console=self.cli,
                refresh_per_second=10,
                transient=True
            )
            self.live.__enter__()

    def stop_loading(self):
        """Stop loading spinner and display cumulative table"""
        if self.live:
            self.live.__exit__(None, None, None)
            self.live = None

        # Add current test results to history
        if self.current_test_results:
            self.all_results.append(self.current_test_results)
            self.current_test_results = []

        # Print cumulative table
        self.cli.print("\n")  # Add spacing
        table = self.create_cumulative_table()
        self.cli.print(table)
        self.cli.print("\n")  # Add spacing

    def update_loading(self, message: str):
        """Update loading message"""
        if self.spinner:
            self.spinner.text = Text(f"🔄 {message}", style="yellow")

    def update(self, event: Dict[str, Any]):
        """Handle different types of events and update the display accordingly"""

        if event["type"] == "status_update":
            if event["message"] == "done":
                self.stop_loading()
            elif event["message"] == "all_tests_complete":
                self.all_tests_complete = True
                self.export_to_csv()
            else:
                if not self.live:
                    self.start_loading(event["message"])
                else:
                    self.update_loading(event["message"])

        elif event["type"] == "function_call":
            # Store function call details
            self.current_test_results.append([
                event["name"],
                self.format_parameters(event["parameters"]),
                "⏳ Executing..."
            ])

        elif event["type"] == "function_result":
            # Update the last result with actual output
            if self.current_test_results:
                self.current_test_results[-1][-1] = self.format_result(event["content"]["content"])

    def get_input(self, message: str) -> str:
        """Handle input requests if needed"""
        return None


class FunctionStudio:
    def __init__(self, config_path: Path):
        self.cli = ToolCLI(menu_text="🔧 Function Studio\n\nTesting function implementations...")
        self.observer = FunctionStudioObserver(str(config_path))
        self.config_path = config_path
        self.config = self._load_config()
        self.tools: List[Callable] = []
        self.terminal_ops = TerminalOperations(".")

        # Initialize client and engine
        self.client = self._setup_client()
        self.engine = self._setup_engine()
        self.engine.subscribe(self.observer)
        # self.engine.subscribe(CLIObserver(self.cli))

        # Load the tools
        self._load_tools()

        # Load context files if specified
        if "context" in self.config:
            self._load_context_files()

    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration from JSON file"""
        try:
            # Resolve path relative to tests directory
            base_path = Path(__file__).parent
            full_path = base_path / 'tests' / self.config_path
            if not full_path.exists():
                full_path = Path(self.config_path)  # Try absolute path as fallback

            with open(full_path, 'r') as f:
                config = json.load(f)

            # Validate required fields
            if 'import' not in config:
                raise ValueError("Config must contain 'import' field")

            return config
        except Exception as e:
            raise ValueError(f"Error loading config file: {e}")

    def _setup_client(self) -> ClientOpenAI:
        """Set up the OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return ClientOpenAI.create_openai(api_key)


    def _setup_engine(self) -> ToolEngine:
        """Set up the tool engine"""
        # Load system prompt from file if specified
        system_prompt = None
        if 'system_prompt_path' in self.config:
            try:
                with open(self.config['system_prompt_path'], 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load system prompt file: {e}[/yellow]")
        # Fall back to direct system_prompt if specified
        elif 'system_prompt' in self.config:
            system_prompt = self.config.get('system_prompt')

        return ToolEngine(
            self.client,
            model_name=self.config.get('model', 'gpt-4o-mini'),
            system_prompt=system_prompt,
            mode="minimal",
            tools=[]
        )

    def _load_context_files(self):
        """Load context files specified in the config"""
        if not isinstance(self.config["context"], list):
            raise ValueError("Context must be a list of file configurations")

        context_files = []
        for file_config in self.config["context"]:
            if isinstance(file_config, str):
                # Simple string path
                context_files.append(ContextFile(path=file_config))
            elif isinstance(file_config, dict):
                # Dict with path and optional description
                context_files.append(ContextFile(
                    path=file_config["path"],
                    description=file_config.get("description")
                ))
            else:
                raise ValueError(f"Invalid context file configuration: {file_config}")

        # Load each context file
        context_content = []
        for ctx_file in context_files:
            try:
                content = self.terminal_ops.read_file(ctx_file.path)
                context_intro = f"\nContents of {ctx_file.path}"
                if ctx_file.description:
                    context_intro += f" ({ctx_file.description})"
                context_intro += ":\n"
                context_content.append(context_intro)
                context_content.append(content)
            except Exception as e:
                console.print(f"[red]Error loading context file {ctx_file.path}: {str(e)}[/red]")

        # Add context to engine if any files were loaded successfully
        if context_content:
            context_message = "\n".join(context_content)
            self.engine.store.store_string(context_message, "assistant")
            console.print(f"[green]Successfully loaded {len(context_files)} context file(s)[/green]")

    def _parse_import_config(self) -> List[ToolImport]:
        """Parse the import configuration from the config file"""
        # ... (rest of the import parsing code remains the same)
        import_config = self.config['import']
        tools_to_import = []

        if isinstance(import_config, dict):
            # Single import configuration
            module_path = import_config['from']
            relative_import = import_config.get('relative_import', True)

            if 'class' in import_config:
                class_config = import_config['class']
                tools_to_import.append(ToolImport(
                    module_path=module_path,
                    names=import_config.get('methods', []),
                    class_name=class_config['name'],
                    class_args=class_config.get('args', {}),
                    relative_import=relative_import
                ))
            else:
                functions = import_config.get('functions', [import_config.get('function')])
                if isinstance(functions, str):
                    functions = [functions]
                tools_to_import.append(ToolImport(
                    module_path=module_path,
                    names=functions,
                    relative_import=relative_import
                ))

        elif isinstance(import_config, list):
            for config in import_config:
                module_path = config['from']
                relative_import = config.get('relative_import', True)

                if 'class' in config:
                    class_config = config['class']
                    tools_to_import.append(ToolImport(
                        module_path=module_path,
                        names=config.get('methods', []),
                        class_name=class_config['name'],
                        class_args=class_config.get('args', {}),
                        relative_import=relative_import
                    ))
                else:
                    functions = config.get('functions', [config.get('function')])
                    if isinstance(functions, str):
                        functions = [functions]
                    tools_to_import.append(ToolImport(
                        module_path=module_path,
                        names=functions,
                        relative_import=relative_import
                    ))

        return tools_to_import

    def _import_module(self, module_path: str, relative_import: bool) -> Any:
        """Import a module using either relative or absolute imports"""
        try:
            if relative_import:
                return importlib.import_module(f"{module_path}")
            else:
                return importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Could not import module {module_path}: {e}")

    def _get_class_instance_methods(self, instance: Any) -> List[Callable]:
        """Get all wrapped methods from a class instance"""
        methods = []
        for name in dir(instance):
            attr = getattr(instance, name)
            if hasattr(attr, 'output') and callable(attr):
                methods.append(attr)
        return methods

    def _import_tools(self, tool_import: ToolImport) -> List[Callable]:
        """Import tools from a module based on the import configuration"""
        module = self._import_module(tool_import.module_path, tool_import.relative_import)

        if tool_import.class_name:
            # Handle class-based tools
            class_obj = getattr(module, tool_import.class_name)
            instance = class_obj(**(tool_import.class_args or {}))

            if tool_import.names:
                # Import specific methods
                return [getattr(instance, name) for name in tool_import.names]
            else:
                # Import all wrapped methods
                return self._get_class_instance_methods(instance)
        else:
            # Handle function-based tools
            return [getattr(module, name) for name in tool_import.names]

    def _load_tools(self):
        """Load all tools specified in the config"""
        try:
            tool_imports = self._parse_import_config()

            for tool_import in tool_imports:
                imported_tools = self._import_tools(tool_import)
                self.tools.extend(imported_tools)

            # Update engine with imported tools
            self.engine.tool_manager.tools = self.tools
            self.engine.tool_manager.tools_schema = [t.output for t in self.tools]
            self.engine.tool_manager.tools_lookup = {t.funct.__name__: t for t in self.tools}

            # Log success
            tool_names = [t.funct.__name__ for t in self.tools]
            console.print(f"[green]Successfully loaded tools: {', '.join(tool_names)}[/green]")

        except Exception as e:
            console.print(f"[red]Error loading tools: {e}[/red]")
            raise

    def run_tests(self):
        """Run all test cases from the config"""
        console.print(f"[bold blue]Running Function Studio Tests[/bold blue]")

        for i, test_case in enumerate(self.config['test_cases'], 1):
            console.print(f"\n[bold cyan]Test Case {i}/{len(self.config['test_cases'])}[/bold cyan]")
            console.print(Panel(
                Syntax(json.dumps(test_case, indent=2), "json", theme="monokai"),
                title="Test Case"
            ))

            try:
                response = self.engine.execute(test_case['prompt'])
            except Exception as e:
                console.print(f"[red]Error running test case: {e}[/red]")

        # Notify observer that all tests are complete
        self.observer.update({"type": "status_update", "message": "all_tests_complete"})


def main(config_path: Optional[str] = None):
    """Main entry point for the function studio"""
    try:
        if config_path is None:
            raise ValueError("No test configuration file provided")

        studio = FunctionStudio(Path(config_path))
        studio.run_tests()
        return 0

    except ValueError as e:
        console.print(f"[red]Configuration Error: {str(e)}[/red]")
        return 1
    except ImportError as e:
        console.print(f"[red]Import Error: {str(e)}[/red]")
        return 1
    except Exception as e:
        console.print(f"[red]Fatal Error: {str(e)}[/red]")
        console.print_exception()
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Error: Please provide a test configuration file path[/red]")
        sys.exit(1)

    try:
        result = main(sys.argv[1])
        sys.exit(result)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test execution interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Unexpected error: {str(e)}[/red]")
        console.print_exception()
        sys.exit(1)
