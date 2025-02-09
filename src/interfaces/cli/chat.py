from typing import Dict, Optional

from framework.types.engine import Engine


class CLIChat:
    def __init__(self,
                 engine: Engine,
                 context: Optional[Dict[str, str]] = None,):
        """Initialize CLI Chat with configuration"""
        self.engine = engine
        self.context = context or {}

    def run(self):
        """Run the CLI Chat interface"""
        print("CLI Chat Interface")
        print("Available commands:")
        print("1. chat")
        print("2. exit")

        while True:
            command = input("Enter command: ")
            if command == "chat":
                self.chat()
            elif command == "exit":
                break
            else:
                print("Invalid command")
