import uuid
import json
import asyncio
from typing import Any, Optional
from dataclasses import dataclass

from llmgine.bus.bus import MessageBus
from llmgine.llm.context.memory import SimpleChatHistory
from llmgine.llm.models.openai_models import Gpt41Mini
from llmgine.llm.providers.providers import Providers
from llmgine.llm.tools.tool_manager import ToolManager
from llmgine.llm.tools import ToolCall
from llmgine.llm.models.openai_models import OpenAIResponse
from openai.types.chat.chat_completion_message import ChatCompletionMessage

from llmgine.messages.commands import Command, CommandResult
from llmgine.messages.events import Event
from llmgine.ui.cli.cli import EngineCLI
from llmgine.ui.cli.components import EngineResultComponent
from llmgine.llm import SessionID, AsyncOrSyncToolFunction


@dataclass
class YourEngineCommand(Command):
    """Command for the Your Engine."""
    prompt: str = ""


@dataclass
class YourEngineStatusEvent(Event):
    """Event emitted when the status of the engine changes."""
    status: str = ""


@dataclass
class YourEngineToolResultEvent(Event):
    """Event emitted when a tool is executed."""
    tool_name: str = ""
    result: Any = None


class YourEngine:
    def __init__(
        self,
        session_id: SessionID,
        system_prompt: Optional[str] = None,
    ):
        """Initialize the Your Engine.

        Args:
            session_id: The session identifier
            system_prompt: Optional system prompt to set
        """
        self.message_bus: MessageBus = MessageBus()
        self.engine_id: str = str(uuid.uuid4())
        self.session_id: SessionID = SessionID(session_id)
        self.system_prompt = system_prompt or "You are a helpful AI assistant that can use tools to help users."

        # Create components
        self.context_manager = SimpleChatHistory(
            engine_id=self.engine_id, session_id=self.session_id
        )
        self.llm_manager = Gpt41Mini(Providers.OPENAI)
        self.tool_manager = ToolManager(
            engine_id=self.engine_id, session_id=self.session_id, llm_model_name="openai"
        )

        # Set system prompt if provided
        if self.system_prompt:
            self.context_manager.store_string(self.system_prompt, "system")

    async def handle_command(self, command: YourEngineCommand) -> CommandResult:
        """Handle a prompt command with tool usage support.

        Args:
            command: The prompt command to handle

        Returns:
            CommandResult: The result of the command execution
        """
        try:
            # Add user message to history
            self.context_manager.store_string(command.prompt, "user")

            # Loop for potential tool execution cycles
            while True:
                # Get current context
                current_context = await self.context_manager.retrieve()

                # Get available tools
                tools = await self.tool_manager.get_tools()

                # Call LLM
                await self.message_bus.publish(
                    YourEngineStatusEvent(
                        status="Calling LLM", session_id=self.session_id
                    )
                )
                
                response: OpenAIResponse = await self.llm_manager.generate(
                    messages=current_context, tools=tools
                )
                assert isinstance(response, OpenAIResponse), (
                    "response is not an OpenAIResponse"
                )

                # Extract the first choice's message object
                response_message: ChatCompletionMessage = response.raw.choices[0].message
                assert isinstance(response_message, ChatCompletionMessage), (
                    "response_message is not a ChatCompletionMessage"
                )

                # Add the assistant message to history
                await self.context_manager.store_assistant_message(response_message)

                # Check for tool calls
                if not response_message.tool_calls:
                    # No tool calls, break the loop and return the content
                    final_content = response_message.content or ""

                    # Notify status complete
                    await self.message_bus.publish(
                        YourEngineStatusEvent(
                            status="Finished", session_id=self.session_id
                        )
                    )
                    return CommandResult(
                        success=True, result=final_content, session_id=self.session_id
                    )

                # Process tool calls
                for tool_call in response_message.tool_calls:
                    tool_call_obj = ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                    try:
                        # Execute the tool
                        await self.message_bus.publish(
                            YourEngineStatusEvent(
                                status="Executing tool", session_id=self.session_id
                            )
                        )

                        result = await self.tool_manager.execute_tool_call(tool_call_obj)

                        # Convert result to string if needed for history
                        if isinstance(result, dict):
                            result_str = json.dumps(result)
                        else:
                            result_str = str(result)

                        # Store tool execution result in history
                        self.context_manager.store_tool_call_result(
                            tool_call_id=tool_call_obj.id,
                            name=tool_call_obj.name,
                            content=result_str,
                        )

                        # Publish tool execution event
                        await self.message_bus.publish(
                            YourEngineToolResultEvent(
                                tool_name=tool_call_obj.name,
                                result=result_str,
                                session_id=self.session_id,
                            )
                        )

                    except Exception as e:
                        error_msg = f"Error executing tool {tool_call_obj.name}: {str(e)}"
                        print(error_msg)
                        # Store error result in history
                        self.context_manager.store_tool_call_result(
                            tool_call_id=tool_call_obj.id,
                            name=tool_call_obj.name,
                            content=error_msg,
                        )
                
                # After processing all tool calls, loop back to call the LLM again
                # with the updated context (including tool results).

        except Exception as e:
            print(f"ERROR in handle_command: {e}")
            import traceback
            traceback.print_exc()

            return CommandResult(success=False, error=str(e), session_id=self.session_id)

    async def register_tool(self, function: AsyncOrSyncToolFunction):
        """Register a function as a tool.

        Args:
            function: The function to register as a tool
        """
        await self.tool_manager.register_tool(function)

    async def clear_context(self):
        """Clear the conversation context."""
        self.context_manager.clear()

    def set_system_prompt(self, prompt: str):
        """Set a new system prompt.

        Args:
            prompt: The new system prompt
        """
        self.system_prompt = prompt
        self.context_manager.clear()
        self.context_manager.store_string(prompt, "system")


# Custom tool functions for YourEngine
def get_current_time() -> str:
    """Get the current time.
    
    Returns:
        The current time as a string.
    """
    from datetime import datetime
    return f"The current time is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


def calculate_math(expression: str) -> str:
    """Calculate a mathematical expression.
    
    Args:
        expression: The mathematical expression to calculate (e.g., "2 + 2", "10 * 5").
    
    Returns:
        The result of the calculation.
    """
    try:
        # Safely evaluate mathematical expressions
        allowed_names = {
            k: v for k, v in __builtins__.items() 
            if k in ['abs', 'round', 'min', 'max', 'sum', 'pow']
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"The result of {expression} is {result}"
    except Exception as e:
        return f"Error calculating {expression}: {str(e)}"


def search_web(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: The search query.
    
    Returns:
        A simulated web search result.
    """
    return f"Web search results for '{query}': This is a simulated search result. In a real implementation, this would connect to a search API."


async def your_engine(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Simple function interface for YourEngine.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt
    
    Returns:
        The engine's response
    """
    session_id = SessionID(str(uuid.uuid4()))
    engine = YourEngine(session_id, system_prompt)
    
    # Register custom tools
    await engine.register_tool(get_current_time)
    await engine.register_tool(calculate_math)
    await engine.register_tool(search_web)
    
    result = await engine.handle_command(YourEngineCommand(prompt=prompt))
    if result.success:
        return result.result
    else:
        raise Exception(result.error)


async def main(case: int = 1):
    """Main function to run the engine.
    
    Args:
        case: 1 for CLI mode, 2 for function mode
    """
    from llmgine.bootstrap import ApplicationConfig, ApplicationBootstrap

    config = ApplicationConfig(enable_console_handler=False)
    bootstrap = ApplicationBootstrap(config)
    await bootstrap.bootstrap()
    
    if case == 1:
        # CLI mode
        session_id = SessionID("your_engine_session")
        engine = YourEngine(session_id, "You are a helpful AI assistant with access to various tools.")
        
        # Register custom tools
        await engine.register_tool(get_current_time)
        await engine.register_tool(calculate_math)
        await engine.register_tool(search_web)
        
        cli = EngineCLI("your_engine_session")
        cli.register_engine(engine)
        cli.register_engine_command(YourEngineCommand, engine.handle_command)
        cli.register_engine_result_component(EngineResultComponent)
        cli.register_loading_event(YourEngineStatusEvent)
        await cli.main()
        
    elif case == 2:
        # Function mode
        result = await your_engine(
            "What time is it and what is 15 * 7?",
            "You are a helpful assistant that can use tools."
        )
        print(result)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main(1))  # Run in CLI mode by default 