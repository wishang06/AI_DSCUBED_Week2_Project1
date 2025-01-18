import os
from dotenv import load_dotenv
from rich.console import Console
from loguru import logger

from src.framework.clients import ClientOpenAI
from src.framework.core.engine import ToolEngine
from tools.calculator import Calculator
from tools.core.terminal import TerminalOperations
from src.interfaces.cli import ToolCLI
from src.framework.tool_calling import openai_function_wrapper

logger.remove()
logger.add("logs/cli_chat_terminal_{time}.log")

MODEL_NAME = "gpt-4o-mini"
SYSTEM_PROMPT_PATH = "./environment/prompts/terminal_system.md"

def create_client():
    """Create OpenAI client with API key from environment"""
    console = Console()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        return None
    return ClientOpenAI.create_openai(api_key)

def create_tool_engine(client, cli):
    
    with open(SYSTEM_PROMPT_PATH, "r") as file:
        system_prompt = file.read()

    try:
        # Initialize tools
        calc = Calculator()
        terminal = TerminalOperations("./environment")
        
        # Create and configure tool engine with hardcoded model
        engine = ToolEngine(
            client=client,
            model_name=MODEL_NAME,
            system_prompt=system_prompt,
            tools=[
                terminal.list_directory,
                terminal.read_file,
                terminal.write_file,
                terminal.delete_file,
                terminal.create_directory,
                terminal.execute_command,
            ],
            callback=cli
        )
        def engine_tools(engine):
            @openai_function_wrapper(
                function_description="Add an instruction (prompt) the llm prompting engine, it will pick it up in the loop",
                parameter_descriptions={
                    "instruction": "prompt in string format"
                }
            )
            def self_instruct(instruction: str):
                engine.add_instruction(instruction)
                return "Completed"
            engine.add_tool(self_instruct)
        engine_tools(engine)
        return engine
    except Exception as e:
        raise

def main():
    # Initialize CLI with custom menu text
    menu_text = """
Tool-Enabled Chat Interface

Available Tools:
• Calculator - Perform mathematical operations
• File Operations - Manage files and directories
• Notion - Query projects, tasks, and documents

Type 'exit' to quit
"""
    cli = ToolCLI(menu_text=menu_text)
    engine = None
    
    try:
        # Initialize environment
        load_dotenv()
        cli.print_info("Starting tool-enabled chat interface...")
    
        # Create OpenAI client
        cli.print_info("Creating OpenAI client...")
        client = create_client()
        if not client:
            return
        
        cli.print_success("Client created successfully!")
        
        # Create tool engine
        engine = create_tool_engine(client, cli)
        
        # Main chat loop
        count = 1
        while True:
            try:
                # Get user input
                user_input = cli.get_input()

                if user_input.lower() in ['exit', 'quit']:
                    break
                
                cli.add_message(user_input, "You", "blue")
                count += 1
                cli.redraw()
                
                # Process the request
                    # Add the instruction and run the engine
                engine.add_instruction(user_input)
                engine.run()
                
                # Count starting from first message

                # Get all messages since the user's input
                messages = engine.store.retrieve()
                
                # Load all messages into the CLI
                for i in range(count, len(messages)):
                    if isinstance(messages[count], dict):
                        if messages[count].get("role") == "user":
                            cli.add_message(messages[count].get("content"),
                                            "You",
                                            "blue")
                        elif messages[count].get("role") == "assistant":
                            cli.add_message(messages[count].get("content"),
                                            "Assistant",
                                            "green")
                        elif messages[count].get("role") == "tool":
                            cli.add_message(messages[count].get("content")[:500],
                                            "Tool Result",
                                            "yellow")
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
    main()
