from typing import Dict, Any, Optional, List
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.spinner import Spinner
from dataclasses import dataclass, field
from enum import Enum, auto
import asyncio


class MessageType(Enum):
    USER = auto()
    ASSISTANT = auto()
    TOOL_CALL = auto()
    TOOL_RESULT = auto()
    SYSTEM = auto()


@dataclass
class Message:
    content: str
    type: MessageType
    metadata: Dict[str, Any] = field(default_factory=dict)


class ChatInterface:
    """Main chat interface handling display and input"""

    def __init__(self):
        self.console = Console()
        self.session = PromptSession()
        self.messages: List[Message] = []
        self.style = Style.from_dict({
            'prompt': '#00aa00 bold',
            'command': '#0000aa',
            'error': '#aa0000',
        })

    async def get_input(self, prompt: str = "You: ") -> str:
        """Get user input with styled prompt"""
        try:
            # Create formatted prompt
            formatted_prompt = HTML(f'<prompt>{prompt}</prompt> ')

            # Get input asynchronously
            result = await self.session.prompt_async(
                formatted_prompt,
                style=self.style
            )

            return result.strip()

        except (EOFError, KeyboardInterrupt):
            return "exit"

    def display_message(self, message: Message):
        """Display a message with appropriate formatting"""
        # Format based on message type
        if message.type == MessageType.USER:
            self._display_user_message(message)
        elif message.type == MessageType.ASSISTANT:
            self._display_assistant_message(message)
        elif message.type == MessageType.TOOL_CALL:
            self._display_tool_call(message)
        elif message.type == MessageType.TOOL_RESULT:
            self._display_tool_result(message)
        elif message.type == MessageType.SYSTEM:
            self._display_system_message(message)

        # Store message
        self.messages.append(message)

    def _display_user_message(self, message: Message):
        """Display user message"""
        self.console.print(
            Panel(
                message.content,
                title="You",
                border_style="blue",
                expand=False
            )
        )

    def _display_assistant_message(self, message: Message):
        """Display assistant message with markdown support"""
        try:
            # Try to render as markdown
            content = Markdown(message.content)
        except:
            # Fallback to plain text
            content = message.content

        self.console.print(
            Panel(
                content,
                title="Assistant",
                border_style="green",
                expand=False
            )
        )

    def _display_tool_call(self, message: Message):
        """Display tool call with syntax highlighting"""
        self.console.print(
            Panel(
                Syntax(
                    message.content,
                    "json",
                    theme="monokai",
                    word_wrap=True
                ),
                title=f"Tool Call: {message.metadata.get('name', 'Unknown')}",
                border_style="yellow",
                expand=False
            )
        )

    def _display_tool_result(self, message: Message):
        """Display tool execution result"""
        self.console.print(
            Panel(
                message.content,
                title=f"Result: {message.metadata.get('name', 'Unknown')}",
                border_style="yellow",
                expand=False
            )
        )

    def _display_system_message(self, message: Message):
        """Display system message"""
        self.console.print(
            Panel(
                message.content,
                title="System",
                border_style="magenta",
                expand=False
            )
        )

    async def stream_response(self, stream_generator, loading_message: str = "Thinking..."):
        """Display streaming response with loading animation"""
        accumulated_text = ""

        with Live(
                Panel(
                    Spinner("dots", text=loading_message),
                    title="Assistant",
                    border_style="green"
                ),
                console=self.console,
                refresh_per_second=10,
                transient=False
        ) as live:
            async for chunk in stream_generator:
                # Update accumulated text
                if hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content or ""
                    accumulated_text += content

                    try:
                        # Try to render as markdown
                        rendered_content = Markdown(accumulated_text)
                    except:
                        # Fallback to plain text
                        rendered_content = accumulated_text

                    # Update display
                    live.update(
                        Panel(
                            rendered_content,
                            title="Assistant",
                            border_style="green"
                        )
                    )

        # Store final message
        self.messages.append(
            Message(
                content=accumulated_text,
                type=MessageType.ASSISTANT
            )
        )

        return accumulated_text

    def clear_screen(self):
        """Clear the terminal screen"""
        self.console.clear()

    def display_history(self, count: Optional[int] = None):
        """Display chat history, optionally limited to last n messages"""
        messages = self.messages[-count:] if count else self.messages

        for message in messages:
            self.display_message(message)

    def display_error(self, error_message: str):
        """Display error message"""
        self.console.print(
            Panel(
                error_message,
                title="Error",
                border_style="red",
                expand=False
            )
        )
