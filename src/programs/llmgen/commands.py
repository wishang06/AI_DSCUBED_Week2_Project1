from typing import Dict, Callable, List, Optional
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class Command:
    name: str
    description: str
    handler: Callable
    aliases: List[str] = None


class CommandHandler:
    """Handles chat commands and their execution"""

    def __init__(self, chat_interface, chat_instance=None):
        self.chat_interface = chat_interface
        self.chat_instance = chat_instance
        self.commands: Dict[str, Command] = {}
        self.register_default_commands()

    def register_command(self, command: Command):
        """Register a new command"""
        self.commands[command.name] = command
        if command.aliases:
            for alias in command.aliases:
                self.commands[alias] = command

    def handle_command(self, command_input: str) -> bool:
        """Handle a command and return True if handled, False otherwise"""
        parts = command_input.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if command.startswith('/'):
            command = command[1:]  # Remove leading slash
            if command in self.commands:
                try:
                    self.commands[command].handler(*args)
                    return True
                except Exception as e:
                    self.chat_interface.display_error(f"Error executing command: {str(e)}")
                    return True
        return False

    def register_default_commands(self):
        """Register default chat commands"""
        default_commands = [
            Command(
                name="clear",
                description="Clear chat history",
                handler=self._handle_clear,
                aliases=["cls"]
            ),
            Command(
                name="help",
                description="Show help message",
                handler=self._handle_help,
                aliases=["?"]
            ),
            Command(
                name="model",
                description="Switch model (e.g., /model gpt-4)",
                handler=self._handle_model
            ),
            Command(
                name="mode",
                description="Change engine mode (normal, minimal, chain)",
                handler=self._handle_mode
            ),
            Command(
                name="system",
                description="Load new system prompt from file",
                handler=self._handle_system
            ),
            Command(
                name="history",
                description="Show chat history",
                handler=self._handle_history
            ),
            Command(
                name="export",
                description="Export chat history to file",
                handler=self._handle_export
            ),
            Command(
                name="load",
                description="Load chat history from file",
                handler=self._handle_load
            ),
            Command(
                name="tools",
                description="List available tools",
                handler=self._handle_tools
            )
        ]

        for command in default_commands:
            self.register_command(command)

    def _handle_clear(self, *args):
        """Handle clear command"""
        self.chat_interface.messages.clear()
        self.chat_interface.clear_screen()
        self.chat_interface.display_message(
            Message(
                content="Chat history cleared",
                type=MessageType.SYSTEM
            )
        )

    def _handle_help(self, *args):
        """Handle help command"""
        help_text = "Available Commands:\n\n"
        for cmd in sorted(set(self.commands.values()), key=lambda x: x.name):
            aliases = f" ({', '.join(cmd.aliases)})" if cmd.aliases else ""
            help_text += f"/{cmd.name}{aliases}\n    {cmd.description}\n\n"

        self.chat.display_message(
            Message(
                content=help_text.strip(),
                type=MessageType.SYSTEM
            )
        )

    def _handle_model(self, *args):
        """Handle model switch command"""
        if not args:
            self.chat.display_error("Please specify a model name")
            return

        try:
            self.chat_instance.engine.model_name = args[0]
            self.chat_interface.display_message(
                Message(
                    content=f"Switched to model: {args[0]}",
                    type=MessageType.SYSTEM
                )
            )
        except Exception as e:
            self.chat.display_error(f"Error switching model: {str(e)}")

    def _handle_mode(self, *args):
        """Handle mode switch command"""
        if not args:
            self.chat.display_error(
                "Please specify a mode (normal, minimal, chain, linear_chain)"
            )
            return

        try:
            self.chat.engine._initialize_mode(args[0])
            self.chat.display_message(
                Message(
                    content=f"Switched to mode: {args[0]}",
                    type=MessageType.SYSTEM
                )
            )
        except Exception as e:
            self.chat.display_error(f"Error switching mode: {str(e)}")

    def _handle_system(self, *args):
        """Handle system prompt change command"""
        if not args:
            self.chat.display_error("Please specify a system prompt file path")
            return

        try:
            path = Path(args[0])
            if not path.exists():
                self.chat.display_error(f"File not found: {path}")
                return

            with open(path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()

            self.chat.engine.store.set_system_prompt(system_prompt)
            self.chat.display_message(
                Message(
                    content=f"Loaded system prompt from: {path}",
                    type=MessageType.SYSTEM
                )
            )
        except Exception as e:
            self.chat.display_error(f"Error loading system prompt: {str(e)}")

    def _handle_history(self, *args):
        """Handle history display command"""
        try:
            # Parse optional count argument
            count = int(args[0]) if args else None
            self.chat.display_history(count)
        except ValueError:
            self.chat.display_error("Invalid count argument")
        except Exception as e:
            self.chat.display_error(f"Error displaying history: {str(e)}")

    def _handle_export(self, *args):
        """Handle export command"""
        try:
            export_path = Path("chat_history.json")
            if args:
                export_path = Path(args[0])

            history = [
                {
                    "content": msg.content,
                    "type": msg.type.name,
                    "metadata": msg.metadata
                }
                for msg in self.chat.messages
            ]

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)

            self.chat.display_message(
                Message(
                    content=f"Chat history exported to: {export_path}",
                    type=MessageType.SYSTEM
                )
            )
        except Exception as e:
            self.chat.display_error(f"Error exporting chat history: {str(e)}")

    def _handle_load(self, *args):
        """Handle load command"""
        if not args:
            self.chat.display_error("Please specify a chat history file path")
            return

        try:
            path = Path(args[0])
            if not path.exists():
                self.chat.display_error(f"File not found: {path}")
                return

            with open(path, 'r', encoding='utf-8') as f:
                history = json.load(f)

            self.chat.messages.clear()
            for msg in history:
                self.chat.messages.append(
                    Message(
                        content=msg["content"],
                        type=MessageType[msg["type"]],
                        metadata=msg.get("metadata", {})
                    )
                )

            self.chat.display_message(
                Message(
                    content=f"Loaded chat history from: {path}",
                    type=MessageType.SYSTEM
                )
            )
            self.chat.display_history()
        except Exception as e:
            self.chat.display_error(f"Error loading chat history: {str(e)}")

    def _handle_tools(self, *args):
        """Handle tools list command"""
        try:
            tools = self.chat.engine.tool_manager.tools
            tool_text = "Available Tools:\n\n"

            for tool in tools:
                tool_text += f"- {tool.funct.__name__}\n"
                tool_text += f"  {tool.function_description}\n\n"

            self.chat.display_message(
                Message(
                    content=tool_text.strip(),
                    type=MessageType.SYSTEM
                )
            )
        except Exception as e:
            self.chat.display_error(f"Error listing tools: {str(e)}")

    def get_command_list(self) -> List[Command]:
        """Get list of all registered commands"""
        return list(set(self.commands.values()))
