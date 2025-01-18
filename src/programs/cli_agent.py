import os

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console

from src.interfaces.cli import ToolCLI
from src.framework.clients import ClientOpenAI
from src.framework.core.engine import LinearAgentEngine
from src.framework.tool_calling import openai_function_wrapper
from tools.core.terminal import TerminalOperations

logger.remove()
logger.add("logs/cli_chat_terminal_{time}.log")

MODEL_NAME = "gpt-4o-mini"
# MODEL_NAME = "google/gemini-flash-1.5-02"
SYSTEM_PROMPT_PATH = "./environment/prompts/terminal_system.md"

def create_client():
    """Create OpenAI client with API key from environment"""
    console = Console()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        return None
    return ClientOpenAI.create_openai(api_key)

# def create_client():
#     """Create openrouter client with API key from environment"""
#     console = Console()
#     api_key = os.getenv("OPENROUTER_API_KEY")
#     if not api_key:
#         console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
#         return None
#     return ClientOpenAI.create_openrouter(api_key)

# def create_client():
#     console = Console()
#     project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
#     region = os.getenv("GOOGLE_CLOUD_REGION")
#     return ClientOpenAI.create_gemini(project_id, region)


def create_tool_engine(client, cli):
    
    with open(SYSTEM_PROMPT_PATH, "r") as file:
        system_prompt = file.read()

    try:
        # Initialize tools
        terminal = TerminalOperations("./environment")
        
        # Create and configure tool engine with hardcoded model
        engine = LinearAgentEngine(
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
                function_description="Add an prompt to your own the prompt queue, this means continuing the execution,\
                    so if you need to get help from the user, you should not call this function.",
                parameter_descriptions={
                    "prompt": "prompt in string format",
                    "explain": "explain what you're going to do\
                        future tense, e.g. 'Im going to call x..."
                }
            )
            def self_prompt(prompt: str, explain: str) -> str:
                engine.queue_prompt("(self-prompted) " + prompt)
                engine.temp = explain
                return f"Prompt added to queue: {prompt}"
            engine.add_agent_tools([self_prompt])
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
                engine.execute_prompt(user_input)
                
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
