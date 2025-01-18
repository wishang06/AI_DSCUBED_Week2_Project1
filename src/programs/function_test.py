import os
from typing import Any, Callable, Dict
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
import json
from pprint import pformat

from src.framework.clients import ClientOpenAI
from src.framework.core.engine import ToolEngine
from src.interfaces.cli import ToolCLI
from src.framework.utils import CLICallback
from tools.core.terminal import TerminalOperations
from tools.notion_abstract import (
    query_database, create_database, update_database,
    create_page, update_page, archive_page, update_block, delete_block,
    search_notion
)

# Initialize Rich console for pretty printing
console = Console()

class FunctionTester:
    """Test harness for trying out individual functions with the LLM framework"""

    def __init__(self, model_name: str = "gpt-4o-mini", mode: str = "chain"):
        """
        Initialize the test harness

        Args:
            model_name: Name of the LLM model to use
            mode: Engine mode ('normal', 'minimal', 'chain', 'linear_chain')
        """
        load_dotenv()

        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = ClientOpenAI.create_openai(self.api_key)
        self.cli = ToolCLI()
        self.callback = CLICallback(self.cli)

        # Initialize engine with specified mode
        self.engine = ToolEngine(
            self.client,
            model_name,
            tools=[],  # Start with empty tools list
            mode=mode,
            callback=self.callback
        )

        # Available function categories
        self.available_functions = {
            'Terminal': {
                'operations': TerminalOperations("./"),
                'functions': [
                    TerminalOperations.list_directory,
                    TerminalOperations.read_file,
                    TerminalOperations.write_file,
                    TerminalOperations.delete_file,
                    TerminalOperations.create_directory,
                    TerminalOperations.execute_command
                ]
            },
            'Notion': {
                'operations': None,
                'functions': [
                    query_database,
                    create_database,
                    update_database,
                    create_page,
                    update_page,
                    archive_page,
                    update_block,
                    delete_block,
                    search_notion
                ]
            }
        }

    def display_function_info(self, func: Callable) -> None:
        """Display detailed information about a function"""
        console.print("\n[bold blue]Function Information:[/bold blue]")

        # Get the OpenAI function schema
        schema = func.output['function']

        # Display basic info
        console.print(f"\n[yellow]Name:[/yellow] {schema['name']}")
        console.print(f"[yellow]Description:[/yellow] {schema['description']}")

        # Display parameters
        console.print("\n[yellow]Parameters:[/yellow]")
        for param_name, param_info in schema['parameters']['properties'].items():
            console.print(f"  [cyan]{param_name}[/cyan]:")
            console.print(f"    Type: {param_info['type']}")
            console.print(f"    Description: {param_info['description']}")
            if 'enum' in param_info:
                console.print(f"    Allowed values: {param_info['enum']}")

        # Display required parameters
        if schema['parameters'].get('required'):
            console.print(f"\n[yellow]Required Parameters:[/yellow] {', '.join(schema['parameters']['required'])}")

    def select_category(self) -> str:
        """Let user select a function category"""
        console.print("\n[bold blue]Available Categories:[/bold blue]")
        categories = list(self.available_functions.keys())
        for i, category in enumerate(categories, 1):
            console.print(f"{i}. {category}")

        while True:
            try:
                choice = int(Prompt.ask("\nSelect category number")) - 1
                if 0 <= choice < len(categories):
                    return categories[choice]
                console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a number.[/red]")

    def select_function(self, category: str) -> Callable:
        """Let user select a function from the category"""
        console.print(f"\n[bold blue]Available Functions in {category}:[/bold blue]")
        functions = self.available_functions[category]['functions']
        for i, func in enumerate(functions, 1):
            console.print(f"{i}. {func.funct.__name__}")

        while True:
            try:
                choice = int(Prompt.ask("\nSelect function number")) - 1
                if 0 <= choice < len(functions):
                    return functions[choice]
                console.print("[red]Invalid choice. Please try again.[/red]")
            except ValueError:
                console.print("[red]Please enter a number.[/red]")

    def get_function_args(self, func: Callable) -> Dict[str, Any]:
        """Prompt user for function arguments"""
        schema = func.output['function']
        args = {}

        console.print("\n[bold blue]Enter function arguments:[/bold blue]")
        for param_name, param_info in schema['parameters']['properties'].items():
            while True:
                value = Prompt.ask(
                    f"Enter value for [cyan]{param_name}[/cyan] ({param_info['type']})"
                )

                # Handle different parameter types
                try:
                    if param_info['type'] == 'integer':
                        value = int(value)
                    elif param_info['type'] == 'number':
                        value = float(value)
                    elif param_info['type'] == 'boolean':
                        value = value.lower() in ('true', 't', 'yes', 'y', '1')
                    elif param_info['type'] == 'object':
                        value = json.loads(value)
                    elif param_info['type'] == 'array':
                        value = json.loads(value)

                    args[param_name] = value
                    break
                except (ValueError, json.JSONDecodeError):
                    console.print(f"[red]Invalid {param_info['type']} value. Please try again.[/red]")

        return args

    def construct_prompt(self, func: Callable, args: Dict[str, Any]) -> str:
        """Construct a natural language prompt for the function call"""
        schema = func.output['function']

        # Start with the function's description
        prompt = f"I want to {schema['description'].lower()}. "

        # Add details about the provided arguments
        prompt += "Here are the details:\n"
        for param_name, value in args.items():
            param_desc = schema['parameters']['properties'][param_name]['description']
            prompt += f"- {param_desc}: {value}\n"

        prompt += "\nCan you help me with this?"
        return prompt

    def display_results(self, response: Any) -> None:
        """Display the results of the function execution"""
        console.print("\n[bold blue]Function Call Results:[/bold blue]")

        # Display the full response
        console.print("\n[yellow]Full Response:[/yellow]")
        console.print(Panel(
            Syntax(pformat(response.full.__dict__, indent=2), "python", theme="monokai"),
            title="Response Object"
        ))

        # Display content if present
        if response.content:
            console.print("\n[yellow]Response Content:[/yellow]")
            console.print(Panel(response.content, title="Content"))

        # Display tool calls if present
        if response.tool_calls:
            console.print("\n[yellow]Tool Calls:[/yellow]")
            for call in response.tool_calls:
                console.print(Panel(
                    Syntax(pformat(call.__dict__, indent=2), "python", theme="monokai"),
                    title=f"Tool Call: {call.function.name}"
                ))

    def run_test(self) -> None:
        """Main test execution loop"""
        while True:
            try:
                # Select category and function
                category = self.select_category()
                func = self.select_function(category)

                # Display function information
                self.display_function_info(func)

                # Get function arguments
                args = self.get_function_args(func)

                # Construct the prompt
                prompt = self.construct_prompt(func, args)
                console.print("\n[bold blue]Generated Prompt:[/bold blue]")
                console.print(Panel(prompt, title="Prompt"))

                # Confirm execution
                if not Confirm.ask("\nProceed with function execution?"):
                    continue

                # Set up engine with single function
                self.engine.tool_manager.tools = [func]
                self.engine.tool_manager.tools_schema = [func.output]
                self.engine.tool_manager.tools_lookup = {func.funct.__name__: func}

                # Execute the function
                response = self.engine._execute(prompt)

                # Display results
                self.display_results(response)

            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]")

            if not Confirm.ask("\nTest another function?"):
                break

def main():
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Test individual functions with LLM framework')
    parser.add_argument('--model', default='gpt-4', help='Name of the LLM model to use')
    parser.add_argument('--mode', default='chain', choices=['normal', 'minimal', 'chain', 'linear_chain'],
                        help='Engine execution mode')
    args = parser.parse_args()

    # Create and run tester
    tester = FunctionTester(model_name=args.model, mode=args.mode)
    tester.run_test()

if __name__ == "__main__":
    main()
