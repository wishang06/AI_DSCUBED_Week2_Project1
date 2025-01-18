import os
from dotenv import load_dotenv
from rich.console import Console

from src.framework.clients import ClientOpenAI
from src.framework.core.engine import ToolEngine
from tools.calculator import Calculator
from tools.core.terminal import TerminalOperations
from tools.notion import (
    query_projects_database,
    get_project_tasks,
    get_project_documents,
    read_document
)
from src.interfaces.cli import ToolCLI

# import logfire

# logfire.configure()

MODEL_NAME = "gpt-4o-mini"

def create_client():
    """Create OpenAI client with API key from environment"""
    console = Console()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Error: OPENAI_API_KEY environment variable not set[/red]")
        return None
    return ClientOpenAI.create_openai(api_key)

def create_tool_engine(client, cli):
    
    # Default system prompt
    system_prompt = """You are a helpful assistant with access to the following tools:

1. Calculator: Perform mathematical operations
   - add: Add two numbers
   - subtract: Subtract two numbers
   - multiply: Multiply two numbers
   - divide: Divide two numbers
   - square_root: Calculate square root
   - power: Calculate power of a number

2. File Operations: Manage files and directories
   - list_directory: List contents of a directory
   - read_file: Read contents of a file
   - write_file: Write content to a file
   - delete_file: Delete a file
   - create_directory: Create a directory

3. Notion: Query projects database, get tasks, documents, and read documents
    - query_projects_database: Query projects database
    - get_project_tasks: Get tasks for a project
    - get_project_documents: Get documents for a project
    - read_document: Read contents of a document

Please use these tools when appropriate to help users with their tasks.
For calculations, always show your work using the calculator tool.
For file operations, always confirm before making changes."""

    try:
        # Initialize tools
        calc = Calculator()
        file_ops = TerminalOperations()
        
        # Create and configure tool engine with hardcoded model
        engine = ToolEngine(
            client=client,
            model_name=MODEL_NAME,
            system_prompt=system_prompt,
            tools=[
                calc.add,
                calc.subtract,
                calc.multiply,
                calc.divide,
                calc.square_root,
                calc.power,
                file_ops.list_directory,
                file_ops.read_file,
                file_ops.write_file,
                file_ops.delete_file,
                file_ops.create_directory,
                query_projects_database,
                get_project_tasks,
                get_project_documents,
                read_document
            ],
            callback=cli
        )
    
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
