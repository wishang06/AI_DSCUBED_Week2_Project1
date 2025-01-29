# src/programs/llmgen/rich_version/commands_streaming.py

from typing import Dict, Callable
import re


class StreamingCommandRegistry:
    """
    A slash-command registry for the streaming chat.
    E.g. /help, /exit, /clear, /model, /mode, ...
    """

    def __init__(self, chat_instance):
        self.chat = chat_instance
        self.commands = {
            "/exit": self.handle_exit,
            "/help": self.handle_help,
            "/clear": self.handle_clear,
            "/model": self.handle_model,
            "/mode": self.handle_mode,
            "/system": self.handle_system_prompt,
            "/tools": self.handle_tools,
        }

    def handle_command(self, command_line: str) -> bool:
        """
        Check if the input is a known slash command.
        Return True if it was handled, else False.
        """
        parts = command_line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            self.commands[cmd](args)
            return True
        return False

    def handle_exit(self, args: str):
        """Exit the chat."""
        self.chat.console.print("[bold red]Exiting...[/bold red]")
        raise KeyboardInterrupt

    def handle_help(self, args: str):
        """Show help text."""
        help_text = """
[bold blue]Available Commands:[/bold blue]
/help - Show this help message
/exit - Exit the program
/clear - Clear the screen & chat history
/model <model_name> - Switch to a different model
/mode <mode> - Change the engine mode (normal, minimal, chain, linear_chain, etc.)
/system <file_path> - Load a system prompt from a file
/tools - List available tools
"""
        self.chat.console.print(help_text)

    def handle_clear(self, args: str):
        """Clear chat screen & engine context."""
        self.chat.console.clear()
        self.chat.engine.store.clear()
        self.chat.console.print("[bold magenta]Chat cleared.[/bold magenta]")

    def handle_model(self, args: str):
        """Switch to a different model."""
        if not args:
            self.chat.console.print("[red]Usage: /model <model_name>[/red]")
            return
        self.chat.engine.model_name = args.strip()
        self.chat.console.print(f"[green]Switched to model: {args.strip()}[/green]")

    def handle_mode(self, args: str):
        """Switch engine execution mode."""
        if not args:
            self.chat.console.print("[red]Usage: /mode <new_mode>[/red]")
            return
        try:
            self.chat.engine._initialize_mode(args.strip())
            self.chat.console.print(f"[green]Switched to mode: {args.strip()}[/green]")
        except ValueError as e:
            self.chat.console.print(f"[red]Error switching mode: {str(e)}[/red]")

    def handle_system_prompt(self, args: str):
        """Load a new system prompt from a file."""
        if not args:
            self.chat.console.print("[red]Usage: /system <file_path>[/red]")
            return
        try:
            with open(args.strip(), "r", encoding="utf-8") as f:
                new_prompt = f.read()
            self.chat.engine.store.set_system_prompt(new_prompt)
            self.chat.console.print(f"[green]System prompt loaded from {args.strip()}[/green]")
        except Exception as e:
            self.chat.console.print(f"[red]Error loading system prompt: {e}[/red]")

    def handle_tools(self, args: str):
        """List available tools from the engine."""
        if not self.chat.engine.tool_manager.tools:
            self.chat.console.print("[magenta]No tools loaded.[/magenta]")
            return

        self.chat.console.print("[bold magenta]Available Tools:[/bold magenta]")
        for tool in self.chat.engine.tool_manager.tools:
            fn_name = tool.funct.__name__
            desc = tool.function_description
            self.chat.console.print(f"• [bold]{fn_name}[/bold]: {desc}")
