from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Vertical, Horizontal
from textual.widgets import Header, Input, Button, Static, Label, RichLog
from textual.binding import Binding
from textual import events
from textual.message import Message
from textual.worker import Worker, get_current_worker

import os
from typing import Optional, List, Dict, Any
from pathlib import Path
from loguru import logger
from dotenv import load_dotenv

from src.framework.core.engine import ToolEngine
from src.framework.clients import ClientOpenAI
from src.framework.core.observer import Observer
from tools.core.terminal import TerminalOperations
from tools.pwsh import execute_command

# Configure logging
logger.remove()
logger.add("outputs/logs/llmgen_textual.log", rotation="10 MB", level="INFO")
logger.info("Starting Textual LLMGen")

# Constants
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_SYSTEM_PROMPT_PATH = "prompts/core/agents/system.md"


class ChatMessage(Static):
    """A single chat message widget"""

    def __init__(
            self,
            content: str,
            author: str,
            message_type: str = "user",
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.content = content
        self.author = author
        self.message_type = message_type

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(f"{self.author}:", classes=f"author {self.message_type}")
            yield Static(self.content, classes="message-content")


class StatusBar(Static):
    """Status bar widget showing current mode and model"""

    def __init__(self, mode: str, model: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = mode
        self.model = model

    def compose(self) -> ComposeResult:
        yield Static(f"Mode: {self.mode} | Model: {self.model}", classes="status-text")

    def update_status(self, mode: Optional[str] = None, model: Optional[str] = None):
        if mode:
            self.mode = mode
        if model:
            self.model = model
        self.query_one(".status-text").update(f"Mode: {self.mode} | Model: {self.model}")


class TextualObserver(Observer):
    """Observer for the LLM engine that updates the Textual UI"""

    def __init__(self, app: "LLMGenApp"):
        self.app = app
        self.loading = False

    def update(self, event: Dict[str, Any]):
        if event["type"] == "response":
            self.app.add_message(event["content"], "Assistant", "assistant")
        elif event["type"] == "function_call":
            self.app.add_message(str(event["parameters"]), f"Tool: {event['name']}", "tool")
        elif event["type"] == "function_result":
            self.app.add_message(
                event["content"]["content"],
                f"Result: {event['name']}",
                "tool-result"
            )
        elif event["type"] == "status_update":
            if event["message"] == "done":
                self.loading = False
                self.app.update_status("")
            else:
                self.loading = True
                self.app.update_status(event["message"])

    def get_input(self, event: Any) -> str:
        """Handle input requests from the engine"""
        if event["type"] == "confirm":
            # Show confirmation dialog
            return self.app.show_confirmation(event["message"])
        return self.app.get_input(event["message"])


class LLMGenApp(App):
    """Main Textual application for LLMGen"""

    CSS = """
    Screen {
        layers: base overlay;
    }

    Header {
        dock: top;
        background: $panel;
        color: $text;
        padding: 1;
    }
    
    #chat-container {
        width: 100%;
        height: auto;
        padding: 1;
    }
    
    #input-container {
        dock: bottom;
        height: 3;
    }
    
    #status-bar {
        dock: bottom;
        height: 1;
        background: $panel-lighten-2;
    }
    
    Input {
        width: 100%;
        margin: 0 1;
    }
    
    .author {
        color: $text;
        text-style: italic;
    }
    
    .author.assistant {
        color: $success;
    }
    
    .author.tool {
        color: $warning;
    }
    
    .author.tool-result {
        color: $accent;
    }
    
    .message-content {
        margin-left: 1;
        margin-bottom: 1;
    }
    
    .status-text {
        width: 100%;
        text-align: right;
        padding-right: 1;
    }

    Button {
        margin: 0 1;
    }
    
    #dialog {
        width: 60;
        height: 11;
        border: thick $background 80%;
        background: $surface;
        color: $text;
        layer: overlay;
    }

    #dialog-content {
        height: 100%;
        padding: 1;
        layout: grid;
        grid-size: 2;
        grid-rows: 1fr 3;
    }
    """

    BINDINGS = [
        Binding("ctrl+d", "toggle_dark", "Toggle Dark Mode", show=True),
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("enter", "send", "Send Message", show=False),
    ]

    def __init__(
            self,
            mode: str = "normal",
            model: str = DEFAULT_MODEL,
            system_prompt_path: Optional[str] = DEFAULT_SYSTEM_PROMPT_PATH,
    ):
        super().__init__()
        self.mode = mode
        self.model = model
        self.system_prompt_path = system_prompt_path

        # Initialize engine components
        self.setup_engine()

    def setup_engine(self):
        """Set up the LLM engine and components"""
        # Load API key
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No OPENAI_API_KEY found in environment")

        # Initialize client and terminal operations
        self.client = ClientOpenAI.create_openai(self.api_key)
        self.terminal = TerminalOperations(".")

        # Load system prompt if specified
        system_prompt = None
        if self.system_prompt_path:
            try:
                with open(self.system_prompt_path, 'r', encoding='utf-8') as f:
                    system_prompt = f.read()
            except Exception as e:
                logger.warning(f"Error loading system prompt: {e}")
                system_prompt = "You are a helpful assistant that uses available tools."

        # Initialize engine
        self.engine = ToolEngine(
            client=self.client,
            model_name=self.model,
            tools=[
                self.terminal.list_directory,
                self.terminal.read_file,
                self.terminal.write_file,
                self.terminal.delete_file,
                self.terminal.create_directory,
                execute_command,
            ],
            mode=self.mode,
            system_prompt=system_prompt
        )

        # Add observer
        self.engine.subscribe(TextualObserver(self))

    def compose(self) -> ComposeResult:
        """Create child widgets"""
        yield Header()

        with ScrollableContainer(id="chat-container"):
            yield Vertical(id="message-list")

        yield StatusBar(self.mode, self.model, id="status-bar")

        with Horizontal(id="input-container"):
            yield Input(placeholder="Type a message or command...", id="message-input")
            yield Button("Send", variant="primary", id="send-button")

    def on_mount(self) -> None:
        """Handle app mount"""
        # Focus input
        self.query_one("#message-input").focus()

        # Show welcome message
        self.add_message(
            "Welcome to LLMGen! Type /help for available commands.",
            "System",
            "info"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "send-button":
            self.action_send()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission"""
        self.action_send()

    def add_message(self, content: str, author: str, message_type: str = "user"):
        """Add a new message to the chat"""
        messages = self.query_one("#message-list")
        messages.mount(ChatMessage(content, author, message_type))
        messages.scroll_end(animate=False)

    def update_status(self, message: str):
        """Update the status bar message"""
        status_bar = self.query_one("#status-bar")
        if message:
            status_bar.update_status(mode=f"{self.mode} | {message}")
        else:
            status_bar.update_status(mode=self.mode)

    def action_send(self):
        """Send the current input message"""
        input_widget = self.query_one("#message-input")
        message = input_widget.value.strip()

        if not message:
            return

        # Clear input
        input_widget.value = ""

        # Handle commands
        if message.startswith('/'):
            self.handle_command(message)
            return

        # Add user message
        self.add_message(message, "You")

        # Create worker to process message
        self.process_message_in_background(message)

    def process_message_in_background(self, message: str):
        """Process message in a background worker"""

        def process_message():
            try:
                self.engine.execute(message)
                self.engine.subject.notify({
                    "type": "status_update",
                    "message": "done"
                })
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self.add_message(f"Error: {str(e)}", "System", "error")

        worker = Worker(process_message)
        self.run_worker(worker)

    def handle_command(self, command: str):
        """Handle special commands"""
        parts = command.lower().split()
        cmd = parts[0]
        args = parts[1:]

        try:
            if cmd == '/help':
                self.show_help()
            elif cmd == '/clear':
                self.clear_chat()
            elif cmd == '/model':
                self.change_model(args[0] if args else None)
            elif cmd == '/mode':
                self.change_mode(args[0] if args else None)
            elif cmd == '/system':
                self.change_system_prompt(" ".join(args) if args else None)
            elif cmd == '/tools':
                self.list_tools()
            else:
                self.add_message(f"Unknown command: {cmd}", "System", "error")
        except Exception as e:
            self.add_message(f"Error executing command: {str(e)}", "System", "error")

    def show_help(self):
        """Show help message"""
        help_text = """
Available Commands:
/help - Show this help message
/clear - Clear chat history
/model <name> - Change model
/mode <mode> - Change engine mode
/system <path> - Load new system prompt
/tools - List available tools

Keyboard Shortcuts:
Ctrl+D - Toggle dark mode
Ctrl+Q - Quit application
Enter - Send message
        """
        self.add_message(help_text, "System", "info")

    def clear_chat(self):
        """Clear chat history"""
        self.query_one("#message-list").remove_children()
        self.engine.store.clear()
        self.add_message("Chat history cleared", "System", "info")

    def change_model(self, model: Optional[str]):
        """Change the current model"""
        if not model:
            self.add_message("Please specify a model name", "System", "error")
            return

        self.model = model
        self.engine.model_name = model
        self.query_one("#status-bar").update_status(model=model)
        self.add_message(f"Switched to model: {model}", "System", "info")

    def change_mode(self, mode: Optional[str]):
        """Change the engine mode"""
        if not mode:
            self.add_message(
                "Please specify a mode (normal, minimal, chain, linear_chain)",
                "System",
                "error"
            )
            return

        try:
            self.engine._initialize_mode(mode)
            self.mode = mode
            self.query_one("#status-bar").update_status(mode=mode)
            self.add_message(f"Switched to mode: {mode}", "System", "info")
        except Exception as e:
            self.add_message(f"Error changing mode: {str(e)}", "System", "error")

    def change_system_prompt(self, path: Optional[str]):
        """Change the system prompt"""
        if not path:
            self.add_message("Please specify a system prompt file path", "System", "error")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
            self.engine.store.set_system_prompt(system_prompt)
            self.add_message(f"Loaded system prompt from: {path}", "System", "info")
        except Exception as e:
            self.add_message(f"Error loading system prompt: {str(e)}", "System", "error")

    def list_tools(self):
        """List available tools"""
        tools = self.engine.tool_manager.tools
        tool_list = "\n".join(
            [f"- {t.funct.__name__}: {t.function_description}" for t in tools]
        )
        self.add_message(f"Available tools:\n\n{tool_list}", "System", "info")

    def action_toggle_dark(self) -> None:
        """Toggle dark mode"""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()


def main(
        mode: str = "normal",
        model: str = DEFAULT_MODEL,
        system_prompt: Optional[str] = DEFAULT_SYSTEM_PROMPT_PATH
):
    """Run the Textual LLMGen application"""
    try:
        app = LLMGenApp(
            mode=mode,
            model=model,
            system_prompt_path=system_prompt
        )
        app.run()
    except Exception as e:
        logger.error(f"Error running LLMGen: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
