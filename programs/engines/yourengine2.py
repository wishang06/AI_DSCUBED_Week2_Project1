import uuid
import asyncio
import json
from dataclasses import dataclass
from typing import Optional, Any, List, Dict

from llmgine.bus.bus import MessageBus
from llmgine.llm import SessionID, AsyncOrSyncToolFunction
from llmgine.llm.engine.engine import Engine
from llmgine.llm.models.model import Model
from llmgine.llm.providers.response import LLMResponse
from llmgine.llm.tools.tool_manager import ToolManager
from llmgine.llm.tools import ToolCall
from llmgine.llm.models.openai_models import OpenAIResponse
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from llmgine.llm.context.memory import SimpleChatHistory
from llmgine.messages.commands import Command, CommandResult
from llmgine.messages.events import Event
from llmgine.ui.cli.cli import EngineCLI
from llmgine.ui.cli.components import EngineResultComponent, ToolComponent


@dataclass
class MyCustomEngineCommand(Command):
    """Command for the My Custom Engine."""
    prompt: str = ""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None


@dataclass
class MyCustomEngineStatusEvent(Event):
    """Event emitted when the status of the engine changes."""
    status: str = ""


@dataclass
class MyCustomEngineResultEvent(Event):
    """Event emitted when the engine produces a result."""
    result: str = ""


@dataclass
class MyCustomEngineToolResultEvent(Event):
    """Event emitted when a tool is executed."""
    tool_name: str = ""
    result: Any = None


class MyCustomEngine(Engine):
    """A custom engine that can be extended with your own logic and tools."""
    
    def __init__(
        self,
        model: Any,
        system_prompt: Optional[str] = None,
        session_id: Optional[SessionID] = None,
    ):
        """Initialize the custom engine.
        
        Args:
            model: The LLM model to use
            system_prompt: Optional system prompt
            session_id: Optional session identifier
        """
        self.model = model
        self.system_prompt = system_prompt
        self.session_id = session_id or SessionID(str(uuid.uuid4()))
        self.bus = MessageBus()
        self.engine_id: str = str(uuid.uuid4())
        
        self.tool_manager = ToolManager(
            engine_id=self.engine_id, 
            session_id=self.session_id, 
            llm_model_name="openai"
        )
        
        self.context_manager = SimpleChatHistory(
            engine_id=self.engine_id, 
            session_id=self.session_id
        )

    async def handle_command(self, command: Command) -> CommandResult:
        """Handle a command following the engine pattern.
        
        Args:
            command: The command to handle
            
        Returns:
            CommandResult: The result of the command execution
        """
        try:
            my_command = command if isinstance(command, MyCustomEngineCommand) else MyCustomEngineCommand(**command.__dict__)
            result = await self.execute(my_command.prompt, my_command.temperature, my_command.max_tokens)
            return CommandResult(success=True, result=result, session_id=self.session_id)
        except Exception as e:
            return CommandResult(success=False, error=str(e), session_id=self.session_id)

    async def execute(self, prompt: str, temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """Execute the main logic of the engine with tool support.
        
        Args:
            prompt: The user's prompt
            temperature: 7
            max_tokens: Optional max tokens for generation
            
        Returns:
            The generated response
        """
        try:
            self.context_manager.store_string(prompt, "user")
            
            while True:
                context = await self.context_manager.retrieve()
                
                tools = await self.tool_manager.get_tools()
                
                await self.bus.publish(
                    MyCustomEngineStatusEvent(
                        status="Processing request", 
                        session_id=self.session_id
                    )
                )

                generation_params = {}
                if temperature is not None:
                    generation_params["temperature"] = temperature
                if max_tokens is not None:
                    generation_params["max_completion_tokens"] = max_tokens

                # Generate response from model
                response: OpenAIResponse = await self.model.generate(
                    messages=context, 
                    tools=tools,
                    **generation_params
                )
                
                response_message: ChatCompletionMessage = response.raw.choices[0].message
                
                # Store the assistant message in conversation history
                await self.context_manager.store_assistant_message(response_message)
                
                # Check for tool calls
                if not response_message.tool_calls:
                    final_content = response_message.content or ""
                    
                    await self.bus.publish(
                        MyCustomEngineStatusEvent(
                            status="Completed", 
                            session_id=self.session_id
                        )
                    )
                    
                    # Publish result event
                    await self.bus.publish(
                        MyCustomEngineResultEvent(
                            result=final_content,
                            session_id=self.session_id
                        )
                    )
                    await self.bus.publish(
                        MyCustomEngineStatusEvent(
                            status="",
                            session_id=self.session_id
                        )
                    )
                    await self.bus.publish(
                        MyCustomEngineStatusEvent(
                            status="finished",
                            session_id=self.session_id
                        )
                    )
                    return final_content
                
                # Process tool calls
                for tool_call in response_message.tool_calls:
                    tool_call_obj = ToolCall(
                        id=tool_call.id,
                        name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                    )
                    
                    try:
                        # Execute the tool
                        await self.bus.publish(
                            MyCustomEngineStatusEvent(
                                status="Executing tool", 
                                session_id=self.session_id
                            )
                        )
                        
                        result = await self.tool_manager.execute_tool_call(tool_call_obj)
                        
                        # Convert result to string if needed
                        if isinstance(result, dict):
                            result_str = json.dumps(result)
                        else:
                            result_str = str(result)
                        
                        # Store tool result in conversation history
                        self.context_manager.store_tool_call_result(
                            tool_call_id=tool_call_obj.id,
                            name=tool_call_obj.name,
                            content=result_str
                        )
                        
                        await self.bus.publish(
                            MyCustomEngineToolResultEvent(
                                tool_name=tool_call_obj.name,
                                result=result_str,
                                session_id=self.session_id,
                            )
                        )
                        
                    except Exception as e:
                        error_msg = f"Error executing tool {tool_call_obj.name}: {str(e)}"
                        print(error_msg)
                        
                        # Store error result in conversation history
                        self.context_manager.store_tool_call_result(
                            tool_call_id=tool_call_obj.id,
                            name=tool_call_obj.name,
                            content=error_msg
                        )
                
                
        except Exception as e:
            print(f"ERROR in execute: {e}")
            import traceback
            traceback.print_exc()
            raise e

    async def register_tool(self, function: AsyncOrSyncToolFunction):
        """Register a function as a tool.
        
        Args:
            function: The function to register as a tool
        """
        await self.tool_manager.register_tool(function)
        print(f"Tool registered: {function.__name__}")

    async def clear_context(self):
        """Clear the conversation context."""
        self.context_manager.clear()

    def set_system_prompt(self, prompt: str):
        """Set the system prompt.
        
        Args:
            prompt: The system prompt to set
        """
        self.system_prompt = prompt
        self.context_manager.set_system_prompt(prompt)


async def use_my_custom_engine(
    prompt: str, 
    model: Any,
    system_prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """Convenience function to use the engine directly.
    
    Args:
        prompt: The user's prompt
        model: The LLM model to use
        system_prompt: Optional system prompt
        temperature: Optional temperature for generation
        max_tokens: Optional max tokens for generation
        
    Returns:
        The generated response
    """
    session_id = SessionID(str(uuid.uuid4()))
    engine = MyCustomEngine(model, system_prompt, session_id)
    return await engine.execute(prompt, temperature, max_tokens)


async def main(case: int = 1):
    """Main function to run the engine.
    
    Args:
        case: Which case to run (1 for CLI, 2 for direct function call)
    """
    from llmgine.bootstrap import ApplicationBootstrap, ApplicationConfig
    from llmgine.llm.models.openai_models import Gpt41Mini
    from llmgine.llm.providers.providers import Providers
    
    # Import Project 1 tools
    from tools.project1_tools import Calculator, WebSearch, SlotMachine

    config = ApplicationConfig(enable_console_handler=False)
    bootstrap = ApplicationBootstrap(config)
    await bootstrap.bootstrap()
    
    if case == 1:
        print("Starting My Custom Engine with Project 1 Tools in CLI mode...")
        
        engine = MyCustomEngine(
            model=Gpt41Mini(Providers.OPENAI),
            system_prompt="You are a helpful AI assistant with access to powerful tools. You can calculate math expressions, search the web, and even play a slot machine game! Always be encouraging and provide detailed, helpful responses.",
            session_id=SessionID("my-custom-engine")
        )
        
        print("Registering Project 1 tools...")
        
        calculator = Calculator()
        slot_machine = SlotMachine()
        
        async def calculate_math(expression: str) -> str:
            """Calculate mathematical expressions.
            
            Args:
                expression: The mathematical expression to evaluate (e.g., '2 + 3 * 4')
                
            Returns:
                The result of the calculation
            """
            return await calculator.execute(expression)
        
        async def play_slot_machine(action: str, bet_amount: int = 10) -> str:
            """Play the slot machine game.
            
            Args:
                action: The action to perform (spin, balance, help)
                bet_amount: Amount to bet (1-100 credits, only used with spin action)
                
            Returns:
                The result of the slot machine action
            """
            return await slot_machine.execute(action, bet_amount)
        
        await engine.register_tool(calculate_math)
        await engine.register_tool(play_slot_machine)
        
        cli = EngineCLI(SessionID("my-custom-engine"))
        cli.register_engine(engine)
        cli.register_engine_command(MyCustomEngineCommand, engine.handle_command)
        cli.register_engine_result_component(EngineResultComponent)
        cli.register_loading_event(MyCustomEngineStatusEvent)
        cli.register_component_event(MyCustomEngineToolResultEvent, ToolComponent)
        
        await cli.main()
        
    elif case == 2:
        print("Running My Custom Engine in direct function call mode...")
        
        result = await use_my_custom_engine(
            prompt="Hello! Can you calculate 15 * 23 for me?",
            model=Gpt41Mini(Providers.OPENAI),
            system_prompt="You are a helpful assistant with access to a calculator tool. Use it when users ask for calculations.",
            temperature=0.7
        )
        
        print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main(1)) 