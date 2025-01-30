from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich import box
import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from loguru import logger

from src.framework.core.engine import ToolEngine
from src.framework.core.observer import Observer
from src.framework.clients.openai_client import ClientOpenAI
from src.framework.types.events import EngineObserverEventType
from src.framework.clients.response import StreamedResponseWrapperOpenAI


class MessageType(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"


@dataclass
class Message:
    content: str
    type: MessageType
    metadata: Dict[str, Any] = field(default_factory=dict)


class StreamingObserver(Observer):
    """Enhanced observer for handling streaming responses and tool calls"""

    def __init__(self, chat_interface):
        self.chat = chat_interface
        self.current_stream = None
        self.stream_live = None

    def update(self, event: Dict[str, Any]):
        if event["type"] == EngineObserverEventType.STREAM:
            self._handle_stream_event(event)
        elif event["type"] == EngineObserverEventType.FUNCTION_CALL:
            self._handle_function_call(event)
        elif event["type"] == EngineObserverEventType.FUNCTION_RESULT:
            self._handle_function_result(event)
        elif event["type"] == EngineObserverEventType.STATUS_UPDATE:
            self._handle_status_update(event)

    def _handle_stream_event(self, event: Dict[str, Any]):
        content = event.get("content", "")
        if not self.stream_live:
            self.stream_live = self.chat.start_streaming()

        if content:
            self.chat.update_stream(content)

        if event.get("done", False):
            self.chat.finish_stream()
            self.stream_live = None

    def _handle_function_call(self, event: Dict[str, Any]):
        self.chat.display_message(Message(
            content=f"Calling function: {event['name']}\nParameters: {event['parameters']}",
            type=MessageType.TOOL_CALL,
            metadata={"name": event["name"]}
        ))

    def _handle_function_result(self, event: Dict[str, Any]):
        self.chat.display_message(Message(
            content=str(event["content"].get("content", "")),
            type=MessageType.TOOL_RESULT,
            metadata={"name": event["content"].get("name", "Unknown Tool")}
        ))

    def _handle_status_update(self, event: Dict[str, Any]):
        if event["message"] == "done":
            if self.stream_live:
                self.chat.finish_stream()
                self.stream_live = None
        else:
            self.chat.display_message(Message(
                content=event["message"],
                type=MessageType.SYSTEM
            ))

    def get_input(self, event: Dict[str, Any]) -> str:
        """Handle input requests from the engine"""
        if self.stream_live:
            self.stream_live.__exit__(None, None, None)
            self.stream_live = None

        if event["type"] == EngineObserverEventType.GET_CONFIRMATION:
            return self.chat.get_confirmation(event["message"])
        return self.chat.get_input(event["message"])


class RichChat:
    """Enhanced chat interface with streaming support and rich formatting"""

    def __init__(self):
        self.console = Console()
        self.session = PromptSession()
        self.messages: List[Message] = []
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'command': '#0000aa',
            'error': '#aa0000',
        })
        self.current_live = None

    def display_message(self, message: Message):
        """Display a message with appropriate formatting"""
        try:
            content = message.content
            if message.type in [MessageType.ASSISTANT, MessageType.SYSTEM]:
                try:
                    content = Markdown(message.content)
                except:
                    pass

            title = message.type.value.title()
            if "name" in message.metadata:
                title = f"{title}: {message.metadata['name']}"

            style = {
                MessageType.SYSTEM: "magenta",
                MessageType.USER: "blue",
                MessageType.ASSISTANT: "green",
                MessageType.TOOL_CALL: "yellow",
                MessageType.TOOL_RESULT: "cyan",
                MessageType.ERROR: "red"
            }[message.type]

            self.console.print(Panel(
                content,
                title=title,
                border_style=style,
                box=box.ROUNDED,
                expand=False
            ))

            self.messages.append(message)
        except Exception as e:
            logger.error(f"Error displaying message: {e}")
            self.display_error(f"Error displaying message: {str(e)}")

    def display_error(self, message: str):
        """Display an error message"""
        self.display_message(Message(
            content=message,
            type=MessageType.ERROR
        ))

    async def get_input(self, prompt: str = "You") -> str:
        """Get user input with styled prompt"""
        try:
            with patch_stdout():
                user_input = await self.session.prompt_async(
                    HTML(f'<prompt>{prompt}></prompt> '),
                    style=self.style
                )
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            return "exit"

    def get_confirmation(self, message: str) -> bool:
        """Get yes/no confirmation from user"""
        while True:
            response = self.console.input(f"{message} (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            self.console.print("Please enter 'y' or 'n'")

    def start_streaming(self) -> Live:
        """Start a new streaming session"""
        if self.current_live:
            self.current_live.__exit__(None, None, None)

        self.current_stream_content = ""
        self.current_live = Live(
            Panel(
                Markdown(self.current_stream_content),
                title="Assistant",
                border_style="green",
                box=box.ROUNDED
            ),
            console=self.console,
            refresh_per_second=10,
            transient=False
        )
        self.current_live.__enter__()
        return self.current_live

    def update_stream(self, new_content: str):
        """Update the current streaming content"""
        if self.current_live:
            self.current_stream_content = new_content
            try:
                content = Markdown(new_content)
            except:
                content = new_content

            self.current_live.update(Panel(
                content,
                title="Assistant",
                border_style="green",
                box=box.ROUNDED
            ))

    def finish_stream(self):
        """Finish the current streaming session"""
        if self.current_live:
            self.current_live.__exit__(None, None, None)
            self.current_live = None
            if self.current_stream_content:
                self.messages.append(Message(
                    content=self.current_stream_content,
                    type=MessageType.ASSISTANT
                ))

    def clear_messages(self):
        """Clear all messages"""
        self.messages.clear()
        self.console.clear()


class StreamingChat:
    """Main chat application with streaming support"""

    def __init__(
            self,
            engine: ToolEngine,
            chat_interface: Optional[RichChat] = None
    ):
        self.engine = engine
        self.chat = chat_interface or RichChat()
        self.observer = StreamingObserver(self.chat)
        self.engine.subscribe(self.observer)

    def display_welcome(self):
        """Display welcome message"""
        welcome_text = (
            f"[bold magenta]Welcome to LLMGen Chat![/bold magenta]\n"
            f"Model: {self.engine.model_name}\n"
            f"Type /help for commands or /exit to quit."
        )
        self.chat.display_message(Message(
            content=welcome_text,
            type=MessageType.SYSTEM
        ))

    async def run(self):
        """Run the chat interface"""
        self.display_welcome()

        while True:
            try:
                user_input = await self.chat.get_input()

                if user_input.lower() in ['exit', 'quit', '/exit', '/quit']:
                    self.chat.display_message(Message(
                        content="Goodbye! 👋",
                        type=MessageType.SYSTEM
                    ))
                    break

                if not user_input.strip():
                    continue

                # Store user message
                self.chat.display_message(Message(
                    content=user_input,
                    type=MessageType.USER
                ))

                # Process with engine
                response = await self.engine.create_streaming_completion(
                    self.engine.model_name,
                    self.engine.store.retrieve()
                )

                # Stream response
                self.chat.start_streaming()
                async for chunk in response:
                    if chunk.content:
                        self.chat.update_stream(chunk.content)
                self.chat.finish_stream()

                # Store final response
                self.engine.store.store_string(response.content, "assistant")

            except KeyboardInterrupt:
                confirm = await self.chat.get_input("Do you want to exit? (y/n): ")
                if confirm.lower() in ['y', 'yes']:
                    break
                continue
            except Exception as e:
                logger.error(f"Error in chat loop: {e}")
                self.chat.display_error(f"Error: {str(e)}")


def create_streaming_chat(
        api_key: str,
        model_name: str = "gpt-4o-mini",
        system_prompt: Optional[str] = None
) -> StreamingChat:
    """Create a new streaming chat instance"""
    client = ClientOpenAI.create_openai(api_key)

    engine = ToolEngine(
        client=client,
        model_name=model_name,
        system_prompt=system_prompt or "You are a helpful assistant.",
        stream_output=True
    )

    return StreamingChat(engine)
