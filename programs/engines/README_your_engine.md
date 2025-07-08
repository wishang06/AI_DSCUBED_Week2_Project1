# YourEngine

A custom LLMgine engine that provides tool-enabled AI assistance with a conversational interface.

## Features

- **Tool Integration**: Built-in support for custom tools
- **Conversation Memory**: Maintains context across interactions
- **CLI Interface**: Interactive command-line interface
- **Function Interface**: Simple function call interface for programmatic use
- **Custom Tools**: Includes time, math calculation, and web search tools

## Built-in Tools

### 1. get_current_time()
Returns the current date and time.

### 2. calculate_math(expression: str)
Safely evaluates mathematical expressions.
- Supports basic arithmetic operations
- Includes safety measures against code injection
- Example: "2 + 2", "10 * 5", "sqrt(16)"

### 3. search_web(query: str)
Simulates web search functionality.
- Currently returns simulated results
- Can be extended to connect to real search APIs

## Usage

### CLI Mode
Run the engine in interactive CLI mode:

```bash
cd llmgine/programs/engines
python yourengine.py
```

This will start an interactive session where you can chat with the AI and use tools.

### Function Mode
Use the engine programmatically:

```python
import asyncio
from yourengine import your_engine

async def main():
    result = await your_engine(
        "What time is it and what is 15 * 7?",
        "You are a helpful assistant that can use tools."
    )
    print(result)

asyncio.run(main())
```

### Custom Tool Registration
You can register your own tools:

```python
from yourengine import YourEngine
from llmgine.llm import SessionID

async def my_custom_tool(param: str) -> str:
    """My custom tool.
    
    Args:
        param: A parameter for the tool.
    
    Returns:
        The result of the tool execution.
    """
    return f"Processed: {param}"

# Create engine
session_id = SessionID("my_session")
engine = YourEngine(session_id)

# Register custom tool
await engine.register_tool(my_custom_tool)

# Use the engine
result = await engine.handle_command(YourEngineCommand(prompt="Use my custom tool"))
```

## Configuration

### Environment Variables
Make sure you have your OpenAI API key set:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### System Prompts
You can customize the system prompt when creating the engine:
```python
engine = YourEngine(session_id, "You are a specialized assistant for coding tasks.")
```

## Architecture

The engine follows the LLMgine pattern with:

1. **Commands**: `YourEngineCommand` for handling user input
2. **Events**: `YourEngineStatusEvent` and `YourEngineToolResultEvent` for status updates
3. **Engine Class**: `YourEngine` containing the main logic
4. **Tool Management**: Integrated tool registration and execution
5. **Context Management**: Conversation history and memory

## Extending the Engine

To add new functionality:

1. **New Tools**: Create functions with proper docstrings and register them
2. **Custom Commands**: Add new command classes for specific operations
3. **Enhanced Events**: Create new event types for additional status updates
4. **Model Integration**: Switch to different LLM models by changing the model initialization

## Example Interactions

```
User: What time is it?
Assistant: Let me check the current time for you.
[Tool: get_current_time]
The current time is 2024-01-15 14:30:25

User: Calculate 25 * 4 + 10
Assistant: I'll calculate that mathematical expression for you.
[Tool: calculate_math]
The result of 25 * 4 + 10 is 110

User: Search for information about Python programming
Assistant: I'll search the web for information about Python programming.
[Tool: search_web]
Web search results for 'Python programming': This is a simulated search result. In a real implementation, this would connect to a search API.
``` 