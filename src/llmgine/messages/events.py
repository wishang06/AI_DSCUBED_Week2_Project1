"""Events used in the system.

This module defines events that can be published on the message bus.
Events represent things that have happened in the system.
"""

import inspect
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

from llmgine.llm.tools.types import SessionID
from llmgine.messages.commands import Command, CommandResult
from types import FrameType

@dataclass
class Event:
    """Base class for all events in the system.

    Events represent things that have happened in the system.
    Multiple handlers can process each event.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[SessionID] = None

    def __post_init__(self) -> None:
        # Set the session id to GLOBAL if it is not set
        if self.session_id is None:
            self.session_id = SessionID("ROOT")

        # Add metadata about where this event was created
        tmp: Optional[Any] = inspect.currentframe()
        assert tmp is not None
        frame: FrameType = tmp.f_back
        if frame:
            module = frame.f_globals.get("__name__", "unknown")
            function = frame.f_code.co_name
            line = frame.f_lineno
            self.metadata["emitted_from"] = f"{module}.{function}:{line}"
        else:
            self.metadata["emitted_from"] = "unknown"


@dataclass
class EventHandlerFailedEvent(Event):
    """Event emitted when an event handler fails."""

    event: Optional[Event] = None
    handler: Optional[str] = None
    exception: Optional[Exception] = None


@dataclass
class CommandStartedEvent(Event):
    """Event emitted when a command is started."""

    command: Optional[Command] = None


@dataclass
class CommandResultEvent(Event):
    """Event emitted when a command result is created."""

    command_result: Optional[CommandResult] = None
