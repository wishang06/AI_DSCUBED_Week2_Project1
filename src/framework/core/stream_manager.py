from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from typing import List, Optional
import asyncio
from dataclasses import dataclass
from framework.core.streaming import StreamingEngine, StreamingClientOpenAI


@dataclass
class ToolCall:
    name: str
    arguments: str
    result: Optional[str] = None


class StreamDisplay:
    """Manages the display of streaming content and tool calls"""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.layout = Layout()
        self.setup_layout()
        self.content = ""
        self.tool_calls: List[ToolCall] = []
        self.live: Optional[Live] = None

    def setup_layout(self):
        """Set up the display layout"""
        self.layout.split(
            Layout(name="main", ratio=2),
            Layout(name="tools", ratio=1),
        )

    def create_main_panel(self) -> Panel:
        """Create the main content panel"""
        return Panel(
            Text(self.content),
            title="LLM Response",
            border_style="blue"
        )

    def create_tools_panel(self) -> Panel:
        """Create the tools panel"""
        if not self.tool_calls:
            return Panel(
                "",
                title="Tool Calls",
                border_style="yellow"
            )

        tool_text = ""
        for i, tool in enumerate(self.tool_calls):
            tool_text += f"Tool {i + 1}: {tool.name}\n"
            tool_text += f"Args: {tool.arguments}\n"
            if tool.result:
                tool_text += f"Result: {tool.result}\n"
            tool_text += "\n"

        return Panel(
            Text(tool_text.strip()),
            title="Tool Calls",
            border_style="yellow"
        )

    def update_display(self):
        """Update the live display"""
        self.layout["main"].update(self.create_main_panel())
        self.layout["tools"].update(self.create_tools_panel())

        if self.live:
            self.live.update(self.layout)

    def stream_content(self, content: str):
        """Add new streaming content"""
        self.content += content
        self.update_display()

    def add_tool_call(self, name: str, arguments: str):
        """Add a new tool call"""
        self.tool_calls.append(ToolCall(name=name, arguments=arguments))
        self.update_display()

    def update_tool_result(self, index: int, result: str):
        """Update the result of a tool call"""
        if 0 <= index < len(self.tool_calls):
            self.tool_calls[index].result = result
            self.update_display()

    async def start_streaming(self, generator):
        """Start streaming from a generator"""
        try:
            with Live(self.layout, console=self.console, refresh_per_second=10) as live:
                self.live = live

                async for chunk in generator:
                    self.stream_content(chunk)
                    await asyncio.sleep(0.05)  # Adjust for smooth updates

        finally:
            self.live = None

    def clear(self):
        """Clear the display"""
        self.content = ""
        self.tool_calls = []
        self.update_display()


class StreamManager:
    """Manages the streaming experience"""

    def __init__(self, engine, display: Optional[StreamDisplay] = None):
        self.engine = engine
        self.display = display or StreamDisplay()

    async def process_prompt(self, prompt: str):
        """Process a prompt and display streaming results"""
        # Clear previous display
        self.display.clear()

        # Start streaming
        await self.display.start_streaming(self.engine.stream_response(prompt))

    def add_tool_result(self, tool_index: int, result: str):
        """Add a tool result to the display"""
        self.display.update_tool_result(tool_index, result)


# Example usage:
async def main():
    # Initialize your streaming engine
    import dotenv
    dotenv.load_dotenv()
    import os

    client = StreamingClientOpenAI(os.getenv("OPENAI_API_KEY"))

    engine = StreamingEngine(client, "gpt-4o-mini", [], "You are a helpful assistant.")

    # Create display manager
    manager = StreamManager(engine)

    # Process a prompt
    await manager.process_prompt("Tell me about streaming LLMs")

    # Add tool results if needed
    manager.add_tool_result(0, "Tool execution result")


if __name__ == "__main__":
    asyncio.run(main())
