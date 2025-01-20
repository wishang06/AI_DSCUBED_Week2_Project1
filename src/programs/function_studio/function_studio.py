import json
import importlib
import os
import sys
import inspect
from dataclasses import dataclass
import dotenv
from pathlib import Path
from typing import Any, Optional, List, Dict, Union, Callable
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from loguru import logger

dotenv.load_dotenv()
BASE_PATH = Path(__file__).parent

from src.framework.clients import ClientOpenAI
from src.framework.core.engine import ToolEngine
from src.framework.utils import CLIStatusCallback
from src.interfaces.cli import ToolCLI

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


class FunctionStudio:
    def __init__(self, config_path: Path):
        self.cli = ToolCLI(menu_text="🔧 Function Studio\n\nTesting function implementations...")
        self.callback = CLIStatusCallback(self.cli)
        self.config_path = config_path
        self.config = self._load_config()
        self.tools: List[Callable] = []

        # Initialize client and engine
        self.client = self._setup_client()
        self.engine = self._setup_engine()

        # Load the tools
        self._load_tools()

    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration from JSON file"""
        try:
            # Resolve path relative to tests directory
            full_path = BASE_PATH / 'tests' / self.config_path
            if not full_path.exists():
                full_path = Path(self.config_path)  # Try absolute path as fallback

            with open(full_path, 'r') as f:
                return json.load(f)
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
        return ToolEngine(
            self.client,
            model_name=self.config.get('model', 'gpt-4o-mini'),
            system_prompt=self.config.get('system_prompt'),
            mode="normal",
            callback=self.callback,
            tools=[],
            debug=True
        )

    def _parse_import_config(self) -> List[ToolImport]:
        """Parse the import configuration from the config file"""
        import_config = self.config['import']
        tools_to_import = []

        # Handle different import configurations
        if isinstance(import_config, dict):
            # Single import configuration
            module_path = import_config['from']
            relative_import = import_config.get('relative_import', True)

            # Handle class imports
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
                # Handle function imports
                functions = import_config.get('functions', [import_config.get('function')])
                if isinstance(functions, str):
                    functions = [functions]
                tools_to_import.append(ToolImport(
                    module_path=module_path,
                    names=functions,
                    relative_import=relative_import
                ))

        elif isinstance(import_config, list):
            # Multiple import configurations
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
            if hasattr(attr, 'output') and callable(attr):  # Check for wrapped methods
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
            self.engine.tool_manager.tools.extend(self.tools)
            self.engine.tool_manager.tools_schema = [t.output for t in self.engine.tool_manager.tools]
            self.engine.tool_manager.tools_lookup = {t.funct.__name__: t for t in self.engine.tool_manager.tools}

            # Log success
            tool_names = [t.funct.__name__ for t in self.tools]
            console.print(f"[green]Successfully loaded tools: {', '.join(tool_names)}[/green]")

        except Exception as e:
            console.print(f"[red]Error loading tools: {e}[/red]")
            raise

    def display_test_info(self, test_case: Dict[str, Any]):
        """Display information about the current test case"""
        console.print("\n[bold blue]Test Case Information:[/bold blue]")
        console.print(Panel(
            Syntax(json.dumps(test_case, indent=2), "json", theme="monokai"),
            title="Test Case"
        ))

    def run_tests(self):
        """Run all test cases from the config"""
        console.print(f"[bold blue]Running Function Studio Tests[/bold blue]")
        tool_names = [t.funct.__name__ for t in self.tools]
        console.print(f"Available tools: {', '.join(tool_names)}")

        for i, test_case in enumerate(self.config['test_cases'], 1):
            console.print(f"\n[bold cyan]Test Case {i}/{len(self.config['test_cases'])}[/bold cyan]")
            self.display_test_info(test_case)

            try:
                response = self.engine.execute(test_case['prompt'])
                self.callback.execute(message=response.content,
                                      title="LLM Response",
                                      style="blue")

            except Exception as e:
                console.print(f"[red]Error running test case: {e}[/red]")

            if i < len(self.config['test_cases']):
                if not Confirm.ask("\nContinue to next test case?"):
                    break


def main(config_path: Optional[str] = None):
    """Main entry point for the function studio"""
    try:
        if config_path is None:
            raise ValueError("No test configuration file provided")

        studio = FunctionStudio(Path(config_path))
        studio.run_tests()

    except Exception as e:
        console.print(f"[red]Fatal Error: {e}[/red]")
        return 1
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Error: Please provide a test configuration file path[/red]")
        sys.exit(1)

    sys.exit(main(sys.argv[1]))
