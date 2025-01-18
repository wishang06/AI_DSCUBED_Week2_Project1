from cli import ToolCLI
from rich.spinner import Spinner
from rich.text import Text
import time

# Create a single CLI instance that can be accessed by all functions
cli = ToolCLI(menu_text="""
🚀 Enhanced CLI Demo

Available commands:
- greet: Display a friendly greeting
- process: Run a multi-step process
- exit/quit: Exit the program

Type a command to begin:
""")

def greet():
    """Example command that prints a greeting"""
    cli.print_success("👋 Hello from the greet command!")

def process():
    """Example command that demonstrates updateable loading state"""
    with cli.show_loading("Starting process...") as loading:
        # Simulate multi-step process
        time.sleep(1)
        loading.update_status("Step 1: Initializing...")
        time.sleep(1)
        loading.update_status("Step 2: Processing data...")
        time.sleep(1)
        loading.update_status("Step 3: Finalizing...")
        time.sleep(1)
    cli.print_success("✅ Process completed successfully!")

def main():
    # Register command functions
    cli.load_command(greet)
    cli.load_command(process)
    
    # Show different message types with markdown
    cli.print_message("""# Welcome to the CLI Interface!
    
This interface supports **markdown** formatting including:
- *Italic text*
- **Bold text**
- `Code blocks`
- Lists and more

## Example Code
```python
def hello():
    print("Hello, World!")
```
""", "System", "green")

    cli.print_error("**Error:** Something went wrong!")
    cli.print_success("✅ Operation completed with `status=200`")
    cli.print_info("""### Information
1. First point
2. Second point
3. Third point""")
    cli.print_message("*Custom styled message with markdown*", "Custom", "magenta")
    
    while True:
        try:
            # Get user input
            user_input = cli.get_input()
            
            # Handle exit
            if user_input.lower() in ['exit', 'quit']:
                cli.print_info("Goodbye!")
                break
            
            # Show loading state for unrecognized input
            if user_input.lower() not in cli.command_functions:
                with cli.show_loading("Processing input...") as loading:
                    time.sleep(1)  # Simulate processing
                cli.print_message(f"Unrecognized command: {user_input}", "Echo", "cyan")
            
        except KeyboardInterrupt:
            cli.print_error("Operation cancelled")
            break

if __name__ == "__main__":
    main()
