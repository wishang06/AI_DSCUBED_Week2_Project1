from src.framework.core.observer import Observer
from typing import Any
from src.interfaces.cli import ToolCLI

class CLIObserver(Observer):
    def __init__(self, cli_interface: ToolCLI):
        self.cli_interface = cli_interface
        self.loading = None

    def update(self, event: Any):
        if event["type"] == "response":
            self.cli_interface.print_message(event["content"], event["type"], "green")
        if event["type"] == "function_call":
            self.cli_interface.print_message(event["parameters"], event["name"], "yellow")
        if event["type"] == "function_result":
            self.cli_interface.print_message(event["content"]["content"], event["name"], "yellow")
        if event["type"] == "status_update":
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

    def get_input(self, message: str):
        return self.cli_interface.get_input(message)
