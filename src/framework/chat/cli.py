from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.spinner import Spinner
from dataclasses import dataclass
from framework.utils.singleton import singleton


@dataclass
class LoadingContext:
    """Context manager for loading spinner"""

    live_context: Live
    spinner: Spinner

    def __enter__(self):
        """Enter the context manager"""
        self.live_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager"""
        return self.live_context.__exit__(exc_type, exc_val, exc_tb)

    def update_status(self, status: str):
        """Update the loading spinner status"""
        self.spinner.text = status


@singleton
class RichCLI:
    def __init__(self):
        self.console = Console()
        self.messages = []
        self.layout = Layout()
        self._setup_layout()

    def _setup_layout(self):
        """Initialize the layout structure"""
        self.layout.split(
            Layout(name="chat", ratio=2),
            Layout(name="tools", ratio=1),
        )

    def get_input(self, prompt: str = "You: ") -> str:
        """Get user input with optional custom prompt"""
        try:
            return Prompt.ask(prompt)
        except (KeyboardInterrupt, EOFError):
            return ""

    def get_confirmation(self, message: str) -> bool:
        """Get yes/no confirmation from user"""
        try:
            # If message is a dict, format it nicely
            if isinstance(message, dict):
                formatted_message = (
                    f"\nFunction: {message.get('function', 'Unknown')}\n"
                )
                if "parameters" in message:
                    formatted_message += "Parameters:\n"
                    for key, value in message["parameters"].items():
                        formatted_message += f"  {key}: {value}\n"
                message = formatted_message

            return Confirm.ask(f"{message}\nDo you want to proceed?")
        except (KeyboardInterrupt, EOFError):
            return False

    def print_message(self, content: str, author: str, style: str = "default"):
        """Print a message with author attribution"""
        if not content:
            return

        panel = Panel(
            Markdown(content), title=f"[{style}]{author}[/{style}]", border_style=style
        )
        self.messages.append({"panel": panel, "type": "message"})
        self.redraw()

    def print_tool_call(self, name: str, args: dict, style: str = "yellow"):
        """Print a tool call with its arguments"""
        content = f"Function: {name}\nArguments: {args}"
        panel = Panel(content, title="Tool Call", border_style=style)
        self.messages.append({"panel": panel, "type": "tool"})
        self.redraw()

    def print_reasoning(self, content: str, style: str = "cyan"):
        """Print reasoning content"""
        if not content:
            return

        panel = Panel(Markdown(content), title="Reasoning", border_style=style)
        self.messages.append({"panel": panel, "type": "reasoning"})
        self.redraw()

    def print_error(self, message: str):
        """Print an error message"""
        self.print_message(message, "Error", "red")

    def print_success(self, message: str):
        """Print a success message"""
        self.print_message(message, "Success", "green")

    def print_info(self, message: str):
        """Print an info message"""
        self.print_message(message, "Info", "blue")

    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()
        self.redraw()

    def show_loading(self, initial_status: str = "Processing...") -> LoadingContext:
        """Show a loading spinner with status"""
        spinner = Spinner("dots", text=initial_status, style="yellow")
        live = Live(
            spinner, console=self.console, refresh_per_second=10, transient=True
        )
        return LoadingContext(live_context=live, spinner=spinner)

    def redraw(self):
        """Redraw the entire display"""
        self.console.clear()
        for message in self.messages:
            self.console.print(message["panel"])

    def print_streaming_content(
        self,
        content: str,
        reasoning: Optional[str] = None,
        tool_calls: Optional[list] = None,
    ):
        """Handle streaming content display"""
        if reasoning:
            self.print_reasoning(reasoning)
        if content:
            self.print_message(content, "Assistant", "green")
        if tool_calls:
            for call in tool_calls:
                self.print_tool_call(
                    call.get("name", "Unknown"), call.get("arguments", {})
                )
