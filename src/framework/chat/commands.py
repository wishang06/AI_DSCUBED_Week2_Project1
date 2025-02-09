from typing import Dict, Callable
from pathlib import Path
import json

from framework.clients.model_registry import ModelRegistry
from framework.types.models import ModelInstanceRequest
from framework.clients.model_manager import ModelManager


class CommandHandler:
    """Handles chat commands with improved model management"""

    def __init__(self, chat_instance):
        self.chat = chat_instance
        self.model_registry = ModelRegistry()
        self.model_manager = ModelManager()
        self.commands: Dict[str, Callable] = {
            "/exit": self._handle_exit,
            "/clear": self._handle_clear,
            "/help": self._handle_help,
            "/model": self._handle_model,
            "/system": self._handle_system,
            "/tools": self._handle_tools,
            "/history": self._handle_history,
            "/export": self._handle_export,
            "/load": self._handle_load,
        }

    def handle_command(self, command_input: str) -> bool:
        """Handle a command and return True if handled, False otherwise"""
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command in self.commands:
            self.commands[command](*args)
            return True
        return False

    def _handle_exit(self, *args):
        """Handle the exit command"""
        raise KeyboardInterrupt

    def _handle_clear(self, *args):
        """Handle the clear command"""
        self.chat.engine.store.clear()
        self.chat.cli.clear_messages()
        self.chat.cli.print_info("Chat history cleared! 🧹")

    def _handle_help(self, *args):
        """Handle the help command"""
        help_text = """
Available commands:
- /exit: Exit the program
- /clear: Clear chat history
- /help: Show this menu
- /model <name>: Switch to a different model
- /system <path>: Load new system prompt
- /tools: List available tools
- /history: Show chat history
- /export: Export chat history
- /load: Load chat history

Type your message to begin...
"""
        self.chat.cli.print_info(help_text)

    def _handle_model(self, *args):
        """Handle the model switch command with improved model instance handling"""
        if not args:
            # List available models with their default providers
            models = self.model_registry.list_models()
            model_info = []
            for model_name in models:
                model = self.model_registry.get_model(model_name)
                model_info.append(
                    f"- {model_name} (Default Provider: {model.default_provider.name})"
                )

            self.chat.cli.print_message(
                "Available models:\n" + "\n".join(model_info), "Models", "cyan"
            )
            return

        model_name = args[0]
        # Create model instance request
        request = ModelInstanceRequest(
            model_name=model_name,
        )

        # Get new model instance
        model_instance = self.model_manager.get_model_instance(request)

        # Update chat with new model instance
        self.chat.set_model(model_instance)

        self.chat.cli.print_success(
            f"Switched to model: {str(model_instance.provider.type)}"
        )

    def _handle_system(self, *args):
        """Handle the system prompt change command"""
        if not args:
            self.chat.cli.print_error("Please specify a system prompt file path")
            return

        path = Path(args[0])
        if not path.exists():
            raise FileNotFoundError(f"System prompt file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        self.chat.engine.store.set_system_prompt(system_prompt)
        self.chat.cli.print_success(f"Loaded system prompt from: {path}")

    def _handle_tools(self, *args):
        """Handle the tools list command"""
        tools = getattr(self.chat.engine, "tools", None)
        if not tools:
            self.chat.cli.print_info("No tools available in current engine mode")
            return

        tool_list = "\n".join(
            [
                f"- {t.__name__}: {getattr(t, 'description', 'No description')}"
                for t in tools
            ]
        )
        self.chat.cli.print_message(f"Available tools:\n\n{tool_list}", "Tools", "cyan")

    def _handle_history(self, *args):
        """Handle the history display command"""
        history = self.chat.engine.store.retrieve()
        for msg in history:
            if msg.get("role") == "user":
                self.chat.cli.print_message(msg.get("content"), "User", "blue")
            elif msg.get("role") == "assistant":
                self.chat.cli.print_message(msg.get("content"), "Assistant", "green")
            elif msg.get("role") == "tool":
                self.chat.cli.print_message(
                    msg.get("content"), msg.get("name", "Tool"), "yellow"
                )

    def _handle_export(self, *args):
        """Handle the export command"""
        export_path = Path("chat_history.json")
        if args:
            export_path = Path(args[0])

        history = self.chat.engine.store.retrieve()
        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

        self.chat.cli.print_success(f"Chat history exported to: {export_path}")

    def _handle_load(self, *args):
        """Handle the load command"""
        if not args:
            raise ValueError("Please specify a chat history file path")

        path = Path(args[0])
        if not path.exists():
            raise FileNotFoundError(f"Chat history file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)

        self.chat.engine.store.clear()
        for msg in history:
            if msg.get("role") == "system":
                self.chat.engine.store.set_system_prompt(msg.get("content"))
            else:
                self.chat.engine.store.chat_history.append(msg)

        self.chat.cli.print_success(f"Loaded chat history from: {path}")
