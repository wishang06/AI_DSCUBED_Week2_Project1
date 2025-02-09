from typing import Any
from framework.core.observer import Observer
from interfaces.cli import ToolCLI
from rich.prompt import Confirm
from framework.types.events import EngineObserverEventType


class LLMGenObserver(Observer):
    def __init__(self, cli_interface: ToolCLI):
        self.cli_interface = cli_interface
        self.loading = None
        self.store = None

    def turn_off_updates(self):
        self.store = self.update
        self.update = lambda x: None

    def turn_on_updates(self):
        self.update = self.store
        self.store = None

    def update(self, event: Any):
        if event["type"] == EngineObserverEventType.RESPONSE:
            self.cli_interface.print_message(event["content"], event["type"], "green")
        elif event["type"] == EngineObserverEventType.FUNCTION_CALL:
            self.cli_interface.print_message(event["parameters"], event["name"], "yellow")
        elif event["type"] == EngineObserverEventType.FUNCTION_RESULT:
            self.cli_interface.print_message(event["content"]["content"], event["name"], "yellow")
        elif event["type"] == EngineObserverEventType.STATUS_UPDATE:
            if not self.loading:
                self.loading = self.cli_interface.show_loading(event["message"])
                self.loading.__enter__()
            elif event["message"] == "done":
                if self.loading:
                    self.loading.__exit__(None, None, None)
                    self.loading = None
                else:
                    raise Exception("Loading spinner not initialized.")
            else:
                self.loading.update_status(event["message"])
        elif event["type"] == EngineObserverEventType.AWAITING_STREAM_COMPLETION:
            self.loading.live_context.stop()
            self.cli_interface.print_streamed_message(event['response'])
            self.loading.live_context.start()


    def get_input(self, event: Any):
        if event["type"] == EngineObserverEventType.GET_CONFIRMATION:
            while True:
                self.loading.live_context.stop()
                response = self.cli_interface.get_confirmation(event["message"]).lower().strip()
                self.loading.live_context.start()
                if response in ['yes', 'y']:
                    return True
                elif response in ['no', 'n']:
                    return False
                print("Please enter 'yes' or 'no'")
        return self.cli_interface.get_input(event["message"])
