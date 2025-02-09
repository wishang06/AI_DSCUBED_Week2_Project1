from rich.traceback import install
from loguru import logger

from framework.chat.cli import RichCLI
from framework.chat.commands import CommandHandler
from framework.types.application_events import ApplicationEvent
from framework.types.models import ModelInstance
from framework.types.events import EngineObserverEventType
from framework.core.observer import Observer


class ChatObserver(Observer):
    """Observer for chat events"""

    def __init__(self, cli):
        self.cli = cli
        self.loading = None

    def update(self, event: ApplicationEvent):
        """Handle various event types"""
        if event.event_type == EngineObserverEventType.RESPONSE:
            if "content" in event:
                if hasattr(event["content"], "choices") and event["content"].choices:
                    # Extract content from OpenAI response
                    content = event["content"].choices[0].message.content
                else:
                    # Fallback for other response types
                    content = str(event["content"])
                self.cli.print_message(content, "Assistant", "green")

        elif event["type"] == EngineObserverEventType.FUNCTION_CALL:
            self.cli.print_tool_call(event["name"], event["parameters"])

        elif event["type"] == EngineObserverEventType.FUNCTION_RESULT:
            self.cli.print_message(event["content"]["content"], event["name"], "yellow")

        elif event["type"] == EngineObserverEventType.STATUS_UPDATE:
            if not self.loading:
                self.loading = self.cli.show_loading(event["message"])
                self.loading.__enter__()
            elif event["message"] == "done":
                if self.loading:
                    self.loading.__exit__(None, None, None)
                    self.loading = None
            else:
                self.loading.update_status(event["message"])

    def get_input(self, event: dict) -> str:
        """Handle input requests"""
        if event["type"] == EngineObserverEventType.GET_CONFIRMATION:
            return "yes" if self.cli.get_confirmation(event["message"]) else "no"
        return self.cli.get_input(event["message"])


class Chat:
    """Main chat interface"""

    def __init__(self, engine):
        # Initialize rich console and install traceback handler
        install(
            show_locals=True, width=120, extra_lines=3, theme="monokai", word_wrap=True
        )

        # Initialize components
        self.cli = RichCLI()
        self.engine = engine
        self.model_instance = engine.model
        self.observer = ChatObserver(self.cli)
        self.engine.subscribe(self.observer)
        self.command_handler = CommandHandler(self)

        # Configure logging
        logger.remove()
        logger.add("outputs/logs/chat.log", rotation="10 MB", level="INFO")
        logger.info("Starting Chat Interface")

    def set_model(self, model_instance: ModelInstance):
        """Update the model configuration"""
        self.model_instance = model_instance
        self.engine.change_model(model_instance)
        logger.info(f"Switched to model: {model_instance.model.name}")

    def run(self):
        """Run the chat interface"""
        self.cli.print_info(
            f"Welcome! Using {self.model_instance.model.name} model. "
            "Type /help for available commands."
        )

        while True:
            # Get user input
            user_input = self.cli.get_input()

            # Handle commands
            if user_input.startswith("/"):
                if self.command_handler.handle_command(user_input):
                    continue

            # Process regular message
            self.cli.print_message(user_input, "You", "blue")

            # Execute message
            response = self.engine.execute(user_input)
            self.engine.subject.notify(
                {"type": EngineObserverEventType.STATUS_UPDATE, "message": "done"}
            )

            # Update display
            self.cli.redraw()
