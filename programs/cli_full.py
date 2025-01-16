import os
from dotenv import load_dotenv
from rich.console import Console
from loguru import logger

from src.core.engine import ToolCallEngine
from src.cli.cli import ToolCLI
from src.clients.openai_client import ClientOpenAI
from src.tools.terminal import TerminalOperations
from src.utils.callbacks import CLICallback

load_dotenv()

logger.remove()
logger.add("./logs/test.log")
logger.info("Starting CLI Chat Terminal")

MODEL_NAME = "gpt-4o-mini"
SYSTEM_PROMPT_PATH = "./environment/prompts/terminal_system.md"

console = Console()
api_key = os.getenv("OPENAI_API_KEY")
client = ClientOpenAI.create_openai(api_key)

with open(SYSTEM_PROMPT_PATH, "r") as file:
    system_prompt = file.read()
terminal = TerminalOperations("./environment")



def main():
    # Initialize CLI with custom menu text
    menu_text = """
    Tool-Enabled Chat Interface
    """
    cli = ToolCLI(menu_text=menu_text)
    callback = CLICallback(cli)
    engine = ToolCallEngine(
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

main()