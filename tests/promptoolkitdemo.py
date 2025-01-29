from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.history import FileHistory
from prompt_toolkit.filters import Condition
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.tree import Tree
from rich.text import Text
from rich.style import Style as RichStyle
from rich.live import Live
from rich.traceback import install
from rich.columns import Columns
from rich import box
import time
import os
import random
from datetime import datetime

# Install rich traceback handler
install(show_locals=True)


class RichPromptToolkitDemo:
    def __init__(self):
        # Initialize Rich console
        self.console = Console()

        # Initialize prompt session with history
        history_file = os.path.expanduser('~/.rich_prompt_history')
        self.session = PromptSession(history=FileHistory(history_file))

        # Available commands for auto-completion
        self.commands = [
            'help', 'exit', 'clear', 'demo', 'table', 'progress',
            'syntax', 'markdown', 'tree', 'panel', 'spinner',
            'columns', 'colors', 'layout', 'about', 'status'
        ]
        self.completer = WordCompleter(self.commands)

        # Prompt styling
        self.style = Style.from_dict({
            'prompt': 'ansibrightmagenta bold',
            'command': 'ansibrightcyan',
            'arrow': 'ansibrightgreen',
        })

        # Key bindings setup
        self.kb = KeyBindings()
        self.setup_key_bindings()

        # State management
        self.running = True

    def setup_key_bindings(self):
        @self.kb.add('c-c')
        @self.kb.add('c-q')
        def _(event):
            """Exit when c-c or c-q is pressed."""
            self.running = False
            event.app.exit()

        @self.kb.add('c-l')
        def _(event):
            """Clear screen when c-l is pressed."""
            self.console.clear()

    def get_prompt(self):
        """Generate formatted prompt."""
        return HTML(
            '<prompt>rich-demo</prompt> '
            '<arrow>→</arrow> '
            '<command></command>'
        )

    def create_demo_table(self):
        """Create a rich formatted table."""
        table = Table(
            title="Rich Formatting Examples",
            caption="Various text styles and colors",
            box=box.DOUBLE_EDGE
        )

        table.add_column("Style", style="cyan", no_wrap=True)
        table.add_column("Example", style="magenta")
        table.add_column("Description", style="green")

        table.add_row("Bold", "[bold]Bold Text[/bold]", "Makes text bold")
        table.add_row("Italic", "[italic]Italic Text[/italic]", "Makes text italic")
        table.add_row("Colors", "[red]Red[/red] [blue]Blue[/blue] [green]Green[/green]", "Colored text")
        table.add_row("Background", "[on red]Red Background[/on red]", "Colored background")
        table.add_row("Combined", "[bold red on white]Combined Styles[/bold red on white]", "Multiple styles")

        return table

    def show_progress_demo(self):
        """Demonstrate Rich progress bars."""
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
        ) as progress:
            task1 = progress.add_task("[red]Processing...", total=100)
            task2 = progress.add_task("[green]Analyzing...", total=100)
            task3 = progress.add_task("[blue]Loading...", total=100)

            while not progress.finished:
                progress.update(task1, advance=random.uniform(0, 2))
                progress.update(task2, advance=random.uniform(0, 1.5))
                progress.update(task3, advance=random.uniform(0, 1))
                time.sleep(0.1)

    def show_syntax_demo(self):
        """Show syntax highlighting demo."""
        code = '''
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    else:
        a, b = 0, 1
        for _ in range(n - 1):
            a, b = b, a + b
        return b

# Example usage
result = fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")
        '''

        syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, title="Python Syntax Highlighting", border_style="green"))

    def show_tree_demo(self):
        """Create and display a sample tree structure."""
        tree = Tree("🌟 Project Structure", style="bold yellow")

        src = tree.add("📁 src", style="blue")
        src.add("📄 main.py", style="green")
        src.add("📄 utils.py", style="green")

        tests = tree.add("📁 tests", style="blue")
        tests.add("📄 test_main.py", style="green")
        tests.add("📄 test_utils.py", style="green")

        docs = tree.add("📁 docs", style="blue")
        docs.add("📄 README.md", style="green")
        docs.add("📄 API.md", style="green")

        return tree

    def show_layout_demo(self):
        """Demonstrate Rich layout capabilities."""
        layout = Layout()

        layout.split_column(
            Layout(Panel("Header", style="on blue"), size=3),
            Layout(name="main"),
            Layout(Panel("Footer", style="on blue"), size=3)
        )

        layout["main"].split_row(
            Layout(Panel("Left Sidebar", title="Navigation", border_style="red")),
            Layout(Panel("Main Content Area", title="Content", border_style="green")),
            Layout(Panel("Right Sidebar", title="Details", border_style="blue"))
        )

        return layout

    def process_command(self, command):
        """Process user input and execute corresponding command."""
        cmd = command.strip().lower()

        if cmd == 'exit':
            self.running = False
            self.console.print("[yellow]Goodbye! Thanks for trying the demo![/yellow]")
            return

        elif cmd == 'help':
            help_text = """
# Available Commands

## Basic Commands
* `help` - Show this help message
* `exit` - Exit the application
* `clear` - Clear the screen
* `about` - Show information about this demo

## Rich Demos
* `table` - Show formatted table demo
* `progress` - Show progress bars demo
* `syntax` - Show syntax highlighting demo
* `markdown` - Show markdown rendering
* `tree` - Show tree structure demo
* `panel` - Show panels demo
* `spinner` - Show spinner demo
* `columns` - Show columns layout
* `colors` - Show available colors
* `layout` - Show layout demo

## Key Bindings
* `Ctrl+C`, `Ctrl+Q` - Exit
* `Ctrl+L` - Clear screen
* `Tab` - Auto-complete commands
* `Up/Down` - Navigate command history
            """
            self.console.print(Markdown(help_text))

        elif cmd == 'clear':
            self.console.clear()

        elif cmd == 'table':
            self.console.print(self.create_demo_table())

        elif cmd == 'progress':
            self.show_progress_demo()

        elif cmd == 'syntax':
            self.show_syntax_demo()

        elif cmd == 'tree':
            self.console.print(self.show_tree_demo())

        elif cmd == 'layout':
            self.console.print(self.show_layout_demo())

        elif cmd == 'markdown':
            markdown = """
# Rich Markdown Demo

This is a demonstration of Rich's Markdown rendering capabilities.

## Features

* **Bold text** and *italic text*
* [Links](https://example.com)
* Lists and nested lists
  * Nested item 1
  * Nested item 2
* Code blocks

```python
def hello_world():
    print("Hello, World!")
```

> Block quotes are also supported!
            """
            self.console.print(Markdown(markdown))

        elif cmd == 'panel':
            panels = [
                Panel("Panel 1", title="Basic", border_style="red"),
                Panel("Panel 2", title="Info", border_style="blue"),
                Panel("Panel 3", title="Success", border_style="green")
            ]
            self.console.print(Columns(panels))

        elif cmd == 'spinner':
            with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    transient=True
            ) as progress:
                task = progress.add_task("Processing...", total=None)
                for _ in range(100):
                    time.sleep(0.1)

        elif cmd == 'columns':
            data = [[Text(f"Row {i}, Col {j}") for j in range(3)] for i in range(4)]
            for row in data:
                self.console.print(Columns(row))

        elif cmd == 'colors':
            colors = ["red", "green", "blue", "magenta", "cyan", "yellow"]
            examples = [Text(f"■ {color}", style=color) for color in colors]
            self.console.print(Columns(examples))

        elif cmd == 'about':
            about_panel = Panel(
                """[bold]Rich + Prompt Toolkit Demo[/bold]

This application demonstrates the powerful combination of:
* [blue]Prompt Toolkit[/blue] for interactive command input
* [green]Rich[/green] for beautiful terminal formatting

Features include:
* Command history and auto-completion
* Syntax highlighting
* Progress bars and spinners
* Tables and panels
* Tree structures
* Markdown rendering
* And much more!""",
                title="About",
                border_style="cyan",
                padding=(1, 2)
            )
            self.console.print(about_panel)

        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")

    def run(self):
        """Main application loop."""
        # Show welcome message
        welcome = Panel(
            "[bold]Welcome to the Rich + Prompt Toolkit Demo![/bold]\n\n"
            "Type [green]'help'[/green] to see available commands or [red]'exit'[/red] to quit.",
            title="Rich + Prompt Toolkit Demo",
            border_style="cyan"
        )
        self.console.print(welcome)

        while self.running:
            try:
                # Get input from user
                command = self.session.prompt(
                    self.get_prompt(),
                    completer=self.completer,
                    style=self.style,
                    key_bindings=self.kb
                )

                # Process the command
                self.process_command(command)

            except KeyboardInterrupt:
                continue
            except EOFError:
                break


if __name__ == '__main__':
    demo = RichPromptToolkitDemo()
    demo.run()
