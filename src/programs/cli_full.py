import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from loguru import logger

from src.framework.core.engine import ToolEngine
from src.interfaces.cli import ToolCLI
from src.framework.clients import ClientOpenAI
from tools.core.terminal import TerminalOperations
from src.framework.utils import CLIStatusCallback

load_dotenv()

logger.remove()
logger.add("outputs/logs/test.log")
logger.info("Starting CLI Chat Terminal")

MODEL_NAME = "gpt-4o-mini"
SYSTEM_PROMPT_PATH = "environment/prompts/terminal_system.md"

console = Console()
api_key = os.getenv("OPENAI_API_KEY")
client = ClientOpenAI.create_openai(api_key)

with open(SYSTEM_PROMPT_PATH, "r") as file:
    system_prompt = file.read()
terminal = TerminalOperations("environment")

def main(args):
    # Initialize CLI with custom menu text
    menu_text = """
    Tool-Enabled Chat Interface
    """
    mode = args[0]
    cli = ToolCLI(menu_text=menu_text)
    callback = CLIStatusCallback(cli)
    engine = ToolEngine(
        client,
        MODEL_NAME,
        tools=[
            terminal.list_directory,
            terminal.read_file,
            terminal.write_file,
            terminal.delete_file,
            terminal.create_directory,
            terminal.execute_command,
        ],
        callback=callback,
        mode=mode
    )
    try:
        # Main chat loop
        count = 0
        while True:
            try:
                # Get user input
                user_input = cli.get_input()

                if user_input.lower() in ["exit", "quit"]:
                    break

                cli.add_message(user_input, "You", "blue")
                count += 1
                cli.redraw()

                # Process the request
                # Add the instruction and run the engine
                engine.execute(user_input)

                # Count starting from first message

                # Get all messages since the user's input
                messages = engine.store.retrieve()

                # Load all messages into the CLI
                for i in range(count, len(messages)):
                    if isinstance(messages[count], dict):
                        if messages[count].get("role") == "user":
                            cli.add_message(
                                messages[count].get("content"), "You", "blue"
                            )
                        elif messages[count].get("role") == "assistant":
                            cli.add_message(
                                messages[count].get("content"), "Assistant", "green"
                            )
                        elif messages[count].get("role") == "tool":
                            cli.add_message(
                                messages[count].get("content")[:500],
                                messages[count].get("name"),
                                "yellow",
                            )
                    count += 1

                cli.redraw()

            except KeyboardInterrupt:
                break
            except Exception as e:
                cli.print_error(f"Chat Error: {str(e)}")
                cli.print_info("You can continue chatting or type 'exit' to quit.")

    except KeyboardInterrupt:
        cli.print_info("Interrupted by user.")
    except Exception as e:
        cli.print_error(f"Fatal Error: {str(e)}")
    finally:
        cli.print_info("Goodbye!")

if __name__ == "__main__":
    mode = [sys.argv[1]]
    main(mode)
