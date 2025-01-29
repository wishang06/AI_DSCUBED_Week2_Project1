from pathlib import Path
import importlib.util
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from loguru import logger
from datetime import datetime

from src.framework.workflow.workflow import Workflow, BinaryDecision
from src.framework.core.observer import Observer
from src.interfaces.cli import ToolCLI

# Configure logging
logger.remove()
logger.add("outputs/logs/workflow_studio.log", rotation="10 MB", level="INFO")
logger.info("Starting Workflow Studio")


class WorkflowStudioObserver(Observer):
    """Observer for tracking workflow execution and results"""

    def __init__(self, cli_interface: ToolCLI):
        self.cli = cli_interface
        self.spinner = None
        self.live = None
        self.current_test = 0
        self.all_results = []
        self.current_results = []
        self.all_tests_complete = False

    def create_results_filename(self) -> Path:
        """Create a filename for the results export"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path("src/programs/workflow_studio/results")
        results_dir.mkdir(parents=True, exist_ok=True)
        return results_dir / f"workflow_test_{timestamp}.txt"

    def export_results(self):
        """Export all results to a file"""
        if not self.all_results or not self.all_tests_complete:
            return

        filename = self.create_results_filename()
        with open(filename, 'w', encoding='utf-8') as f:
            for test_num, results in enumerate(self.all_results, 1):
                f.write(f"\nTest #{test_num}\n")
                f.write("-" * 40 + "\n")
                for block_name, result, context in results:
                    f.write(f"\nBlock: {block_name}\n")
                    f.write(f"Result: {result}\n")
                    f.write(f"Context: {context}\n")
                    f.write("-" * 20 + "\n")

        self.cli.print_message(f"Results saved to: {filename}", "Export", "green")

    def create_results_table(self) -> Table:
        """Create a table showing current test results"""
        table = Table(
            title="🔄 Workflow Execution Results",
            show_header=True,
            header_style="bold magenta",
            title_style="bold blue",
            border_style="blue"
        )

        table.add_column("Block", style="cyan")
        table.add_column("Result", style="green")
        table.add_column("Context", style="yellow")

        for block_name, result, context in self.current_results:
            table.add_row(
                block_name,
                str(result),
                str(context)
            )

        return table

    def update(self, event: Dict[str, Any]):
        """Handle different types of workflow events"""
        if event["type"] == "block_start":
            if not self.live:
                self.spinner = Spinner("dots", text=Text(f"🔄 Executing block: {event['block']}", style="yellow"))
                self.live = Live(
                    self.spinner,
                    console=self.cli.console,
                    refresh_per_second=10,
                    transient=True
                )
                self.live.__enter__()
            else:
                self.spinner.text = Text(f"🔄 Executing block: {event['block']}", style="yellow")

        elif event["type"] == "block_complete":
            self.current_results.append((
                event["block"],
                event["result"],
                event.get("context", {})
            ))

            if self.live:
                self.live.__exit__(None, None, None)
                self.live = None

            # Show updated results table
            self.cli.console.print("\n")
            table = self.create_results_table()
            self.cli.console.print(table)
            self.cli.console.print("\n")

        elif event["type"] == "workflow_complete":
            self.all_results.append(self.current_results)
            self.current_results = []

            if event.get("final", False):
                self.all_tests_complete = True
                self.export_results()

    def get_input(self, event: Any) -> str:
        """Handle any input requests from the workflow"""
        # Implement if needed
        return ""


class WorkflowStudio:
    """Main class for testing workflow definitions"""

    def __init__(self):
        self.cli = ToolCLI(menu_text="🔄 Workflow Studio\n\nTesting workflow definitions...")
        self.observer = WorkflowStudioObserver(self.cli)

    def load_workflow_module(self, path: Path) -> Any:
        """Import a workflow definition module"""
        try:
            spec = importlib.util.spec_from_file_location(path.stem, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module spec for {path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            raise ImportError(f"Error importing workflow module {path}: {str(e)}")

    def validate_workflow(self, workflow: Workflow) -> bool:
        """Validate a workflow definition"""
        if not workflow.start:
            raise ValueError("Workflow must have a start block defined")

        # Add more validation as needed
        return True

    def display_workflow_info(self, workflow: Workflow):
        """Display information about the workflow structure"""
        # Create a table showing workflow blocks and their connections
        table = Table(
            title="📋 Workflow Structure",
            show_header=True,
            header_style="bold magenta"
        )

        table.add_column("Block", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Next Blocks", style="yellow")

        for name, block in workflow.blocks.items():
            block_type = "Decision" if isinstance(block, BinaryDecision) else "Block"
            next_blocks = ", ".join(block.next_blocks.keys()) if block.next_blocks else "None"
            table.add_row(name, block_type, next_blocks)

        self.cli.console.print(table)
        self.cli.console.print("\n")

    def run_workflow_test(self, workflow: Workflow, test_input: Dict[str, Any]):
        """Run a single workflow test with given input"""
        try:
            # Initialize workflow context with test input
            workflow.context.update(test_input)

            # Display workflow structure
            self.display_workflow_info(workflow)

            # Run the workflow
            workflow.run()

            # Notify observer of completion
            self.observer.update({
                "type": "workflow_complete",
                "final": True
            })

        except Exception as e:
            self.cli.print_error(f"Error executing workflow: {str(e)}")
            raise


def main(workflow_path: str, test_input: Optional[Dict[str, Any]] = None):
    """Main entry point for workflow studio"""
    try:
        studio = WorkflowStudio()

        # Load workflow module
        workflow_file = Path(workflow_path)
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

        module = studio.load_workflow_module(workflow_file)

        # Get workflow instance
        if not hasattr(module, 'workflow'):
            raise ValueError("Workflow module must define a 'workflow' variable")

        workflow = module.workflow

        # Validate workflow
        studio.validate_workflow(workflow)

        # Run test
        test_input = test_input or {}
        studio.run_workflow_test(workflow, test_input)

        return 0

    except Exception as e:
        Console().print(f"[red]Error running Workflow Studio: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python workflow_studio.py <workflow_file> [test_input_json]")
        sys.exit(1)

    workflow_path = sys.argv[1]
    test_input = {}

    if len(sys.argv) > 2:
        import json

        with open(sys.argv[2], 'r') as f:
            test_input = json.load(f)

    sys.exit(main(workflow_path, test_input))
