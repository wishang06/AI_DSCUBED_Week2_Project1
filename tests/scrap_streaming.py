from framework.clients.model_manager import ModelManager
from framework.types.application_events import (
    StreamingApplicationEvent,
    StreamingEventTypes,
    StreamingChunkTypes,
)
from framework.types.models import ModelInstanceRequest
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich.markdown import Markdown
from rich.columns import Columns


class StreamDisplay:
    """Simple streaming content display"""

    def __init__(self):
        self.reasoning_content = ""
        self.response_content = ""
        self.tool_content = ""

    def get_renderable(self):
        """Get the current display content"""
        panels = []

        # Only show panels that have content
        if self.reasoning_content:
            panels.append(
                Panel(
                    Markdown(self.reasoning_content),
                    title="Reasoning",
                    border_style="yellow",
                )
            )

        if self.response_content:
            panels.append(
                Panel(
                    Markdown(self.response_content),
                    title="Response",
                    border_style="green",
                )
            )

        if self.tool_content:
            panels.append(
                Panel(
                    Markdown(self.tool_content), title="Tool Calls", border_style="blue"
                )
            )

        return Columns(panels) if panels else ""


def console_printer(event: StreamingApplicationEvent, display: StreamDisplay):
    """Process streaming events and update the display"""
    if event.event_type == StreamingEventTypes.STARTED:
        display.response_content = "**Stream started...**\n"

    elif event.event_type == StreamingEventTypes.CHUNK:
        if event.stream_type == StreamingChunkTypes.REASONING:
            display.reasoning_content = event.data["full"]["reasoning"]

        elif event.stream_type == StreamingChunkTypes.TEXT:
            display.response_content = event.data["full"]["content"]

        elif event.stream_type == StreamingChunkTypes.TOOL:
            display.tool_content = f"```json\n{event.data['full']['tool_call']}\n```"

    elif event.event_type == StreamingEventTypes.COMPLETED:
        display.response_content += "\n\n**Stream completed.**"


def main():
    console = Console()
    display = StreamDisplay()

    try:
        model = ModelManager().get_model_instance(
            ModelInstanceRequest("claude-3.5-sonnet")
        )

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Explain the concept of transformers in deep learning.",
            },
        ]

        with Live(
            display.get_renderable(),
            console=console,
            auto_refresh=True,
            vertical_overflow="visible",
        ) as live:

            def wrapped_printer(event: StreamingApplicationEvent):
                console_printer(event, display)
                live.update(display.get_renderable())

            response = model.provider.stream_completion(
                model, context=messages, emitters=wrapped_printer
            )

        console.print(f"\nTokens: {response.usage.total_tokens}")
        console.print(f"Stop reason: {response.stop_reason}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    main()
