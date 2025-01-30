import os
from typing import List, Dict, Optional, Any
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import box
from rich.live import Live
from rich.spinner import Spinner
from rich.pretty import Pretty
from rich.rule import Rule

def wrap_with_thinking(text: str) -> str:
    """Wrap text in thinking emoji."""
    return f"<thinking>\n{text}\n</thinking>\n"


class ToolCLI:
    """Simplified CLI interface with menu, messages, and loading states."""
    
    def __init__(self, menu_text: Optional[str] = None):
        self.console = Console()
        self.commands = []
        self.messages = []  # Store all messages to redraw
        self.command_functions = {}  # Store command functions
        
        # Default menu text if none provided
        self.menu_text = menu_text or """
🔧 Command Interface

Type 'help' for available commands
Type 'exit' to quit
"""

    def clear_messages(self):
        """Clear all stored messages."""
        self.messages = []

    def add_message(self, content: str, author: str, style: str):
        """Add a message to the message list."""
        self.messages.append({"content": content, "author": author, "style": style})

    def redraw(self):
        """Clear screen and redraw all content."""
        self.clear_terminal()

        # Print menu once at the top
        self.console.print(Panel(
            Text(self.menu_text, justify="center", style="bold white"),
            title="Command Interface",
            subtitle="v1.0",
            border_style="blue",
            box=box.HEAVY
        ))

        # Print all stored messages
        for msg in self.messages:
            try:
                # Try to render as markdown first
                content = Markdown(msg["content"])
            except Exception:
                # Fall back to plain text if markdown parsing fails
                content = Text(msg["content"], style=msg["style"])
            
            self.console.print(Panel(
                content,
                title=msg["author"],
                border_style=msg["style"],
                box=box.ROUNDED
            ))

    def print_message(self, content: str, author:str, style: str):
        """Print a boxed message with an author."""
        msg = {"content": content, "author": author, "style": style}
        try:
            # Try to render as markdown first
            content = Markdown(msg["content"])
        except Exception:
            try:
            # Fall back to plain text if markdown parsing fails
                content = Text(msg["content"], style=msg["style"])
            except Exception:
                content = Pretty(msg["content"], expand_all=True)

        self.console.print(Panel(
            content,
            title=msg["author"],
            border_style=msg["style"],
            box=box.ROUNDED
        ))

    def print_streamed_message(self, response: Any):
        # todo find proper type for response
        """Print a message that updates live within a panel."""
        with Live(None, vertical_overflow='visible', auto_refresh=True) as live:
            for chunk in response:
                if response.reasoning:
                    live.update(
                        Panel(Markdown(wrap_with_thinking(response.reasoning)+response.content), style="green",
                              title="Assistant"))
                if response.content:
                    live.update(Panel(Markdown(response.content), border_style="green", title="Assistant"))
                if response.response_tool_stream:
                    live.update(Panel(Markdown(response.response_tool_stream), border_style="green", title="Assistant"))


    def add_and_redraw(self, content: str, author: str, style: str = "blue"):
        """Print a boxed message with an author."""
        message = {"content": content, "author": author, "style": style}
        self.messages.append(message)
        self.redraw()

    def show_loading(self, message: str = "Processing..."):
        """
        Show a loading spinner with updateable message.
        Returns a context manager that can be used to update the loading message.
        
        Example:
            with cli.show_loading("Initial message...") as loading:
                # Do some work
                loading.update("Step 1...")
                # Do more work
                loading.update("Step 2...")
        """
        spinner = Spinner("dots", text=Text(message, style="yellow"))
        live = Live(
            spinner,
            console=self.console,
            refresh_per_second=10,
            transient=True
        )
        
        class LoadingContext:
            def __init__(self, live_context, spinner):
                self.live_context = live_context
                self.spinner = spinner
            
            def __enter__(self):
                self.live_context.__enter__()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                return self.live_context.__exit__(exc_type, exc_val, exc_tb)
            
            def update_status(self, new_message: str):
                """Update the loading message."""
                self.spinner.text = Text(new_message, style="yellow")
        
        return LoadingContext(live, spinner)

    def get_input(self, prompt: str = "You") -> str:
        """Get input from user and store command."""
        # Create a gradient prompt
        self.console.print(Rule(
            title=f"[bold blue]{prompt}[/bold blue]",
            style="blue",
        ))
        user_input = self.console.input("❯ ")
        
        if user_input.lower() not in ['exit', 'quit']:
            self.commands.append(user_input)
            # Add user input as a message
            self.print_message(user_input, prompt, "blue")
        # Check if input matches a registered command function
        if user_input.lower() in self.command_functions:
            try:
                self.command_functions[user_input.lower()]()
            except Exception as e:
                self.print_error(f"Error executing command: {str(e)}")
        self.clear_terminal()
        self.redraw()
        return user_input

    def get_confirmation(self, prompt: str = "You") -> str:
        """Get input from user and store command."""
        self.console.print(Panel(Pretty(prompt, expand_all=True), title="[bold]Confirmation function call? (y/n)[/bold]", border_style="yellow"))
        user_input = self.console.input("❯ ")
        return user_input

    def load_command(self, func) -> None:
        """
        Register a function to be executed when its name is typed as a command.
        The function name will be converted to lowercase for case-insensitive matching.
        
        Args:
            func: The function to register as a command
        """
        command_name = func.__name__.lower()
        self.command_functions[command_name] = func

    def clear_terminal(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_command_history(self) -> List[str]:
        """Get list of stored commands."""
        return self.commands

    def print_error(self, message: str):
        """Print an error message."""
        self.print_message(message, "Error", "red")

    def print_info(self, message: str):
        """Print an info message."""
        self.print_message(message, "Info", "yellow")

    def print_success(self, message: str):
        """Print a success message."""
        self.print_message(message, "Success", "green")
