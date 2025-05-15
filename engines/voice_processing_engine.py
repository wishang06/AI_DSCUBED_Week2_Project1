"""
This engine's job is to receive facts and decides whether to
create, update, or delete a fact.

To create or update a fact, construct the content as follows:
<CREATE_FACT><fact>

To delete a fact, construct the content as follows:
<DELETE_FACT><fact>
"""

from dataclasses import dataclass
from typing import Optional
import uuid
import json

from llmgine.llm.engine.engine import Engine
from llmgine.llm.models.model import Model
from llmgine.messages.commands import Command, CommandResult
from llmgine.bus.bus import MessageBus
from llmgine.messages.events import Event
from llmgine.llm.tools.tool_manager import ToolManager
from llmgine.llm.models.openai_models import Gpt41Mini
from llmgine.llm.providers.providers import Providers
from llmgine.llm.context.memory import SimpleChatHistory
from llmgine.llm.tools import ToolCall, Tool
from llmgine.ui.cli.voice_processing_engine_cli import SpecificPrompt, SpecificComponent, SpecificPromptCommand, SpecificComponentEvent

from programs.Audio2Text.transcribe import process_audio
from programs.Audio2Text.transcribe import merge_speakers

SYSTEM_PROMPT = f'You are a voice processing engine. You are provided with the number of speakers inside the conversation, '\
f'and a snippet of what each speaker said in the conversation. '\
f'The number of speakers present in the snippet will be greater than the actual number of speakers in the conversation. '\
f'Your task is to decide which speakers in the snippet should be merged into a single speaker, based on the context, speaking style, '\
f'and the content of what they said. '\


# ----------------------------------CUSTOM DATACLASSES-----------------------------------

@dataclass
class VoiceProcessingEngineCommand(Command):
    prompt: str = ""


@dataclass
class VoiceProcessingEngineStatusEvent(Event):
    status: str = ""


@dataclass
class VoiceProcessingEngineToolResultEvent(Event):
    tool_name: str = ""
    result: str = ""


# ------------------------------------ENGINE-------------------------------------------


class VoiceProcessingEngine(Engine):
    def __init__(
        self,
        model: Model,
        system_prompt: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.message_bus = MessageBus()
        self.engine_id = str(uuid.uuid4())

        # Create tightly coupled components - pass the simple engine
        self.context_manager = SimpleChatHistory(
            engine_id=self.engine_id, session_id=self.session_id
        )
        self.llm_manager = Gpt41Mini(Providers.OPENAI)
        self.tool_manager = ToolManager(
            engine_id=self.engine_id, session_id=self.session_id, llm_model_name="openai"
        )

    async def handle_command(self, command: VoiceProcessingEngineCommand) -> CommandResult:
        """Handle a prompt command following OpenAI tool usage pattern.

        Args:
            command: The prompt command to handle

        Returns:
            CommandResult: The result of the command execution
        """
        try:
            # Process the audio file and get the snippet
            audio_file, number_of_speakers = command.prompt.split("&")
            snippet = process_audio(audio_file, number_of_speakers)
            # Prompt the LLM with the actual number of speakers and the snippet
            prompt = "Actual Number of speakers: " + number_of_speakers + ".\nHere is the snippet of what each speaker said in the conversation: " + snippet
            result = await self.execute(prompt=prompt)
            
            return CommandResult(success=True, result=result)
        except Exception as e:
            return CommandResult(success=False, error=str(e))



    async def execute(self, prompt: str) -> str:
        """This function executes the engine.
        
        Args:
            prompt: The prompt to execute
        """

        self.context_manager.store_string(prompt, "user")

        while True:
            # Retrieve the current context
            current_context = await self.context_manager.retrieve()
            # Get the tools
            tools = await self.tool_manager.get_tools()
            # Notify status
            await self.message_bus.publish(
                VoiceProcessingEngineStatusEvent(
                    status="calling LLM", session_id=self.session_id
                )
            )
            # Generate the response
            response = await self.llm_manager.generate(
                messages=current_context, tools=tools
            )
            # Get the response message
            response_message = response.raw.choices[0].message
            # Store the response message
            await self.context_manager.store_assistant_message(response_message)
            # If there are no tool calls, break the loop and return the content
            if not response_message.tool_calls:
                final_content = response_message.content or ""
                # Notify status complete
                await self.message_bus.publish(
                    VoiceProcessingEngineStatusEvent(
                        status="finished", session_id=self.session_id
                    )
                )
                return final_content

            # Else, process tool calls
            for tool_call in response_message.tool_calls:
                tool_call_obj = ToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                )
                try:
                    # Execute the tool
                    await self.message_bus.publish(
                        VoiceProcessingEngineStatusEvent(
                            status="executing tool", session_id=self.session_id
                        )
                    )                
                    
                    # Message bus is hidden from the llm, insert it here manually
                    if tool_call.function.name == "send_to_judge" or tool_call.function.name == "deletion_confirmation":
                        args = json.loads(tool_call.function.arguments)
                        args["session_id"] = self.session_id
                        tool_call_obj.arguments = json.dumps(args)
                        
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
                        VoiceProcessingEngineToolResultEvent(
                            tool_name=tool_call_obj.name,
                            result=result_str,
                            session_id=self.session_id,
                        )
                    )

                except Exception as e:
                    error_msg = f"Error executing tool {tool_call_obj.name}: {str(e)}"
                    print(error_msg)  # Debug print
                    # Store error result in history
                    self.context_manager.store_tool_call_result(
                        tool_call_id=tool_call_obj.id,
                        name=tool_call_obj.name,
                        content=error_msg,
                    )

    
    async def register_tool(self, function : Tool):
        """Register a function as a tool.

        Args:
            function: The function to register as a tool
        """
        await self.tool_manager.register_tool(function)


async def main():
    from llmgine.ui.cli.voice_processing_engine_cli import VoiceProcessingEngineCLI
    from llmgine.ui.cli.components import EngineResultComponent, ToolComponent
    from llmgine.bootstrap import ApplicationConfig, ApplicationBootstrap
    from llmgine.llm.models.openai_models import Gpt41Mini
    from llmgine.llm.providers.providers import Providers

    config = ApplicationConfig(enable_console_handler=False)
    bootstrap = ApplicationBootstrap(config)
    await bootstrap.bootstrap()

    # Initialize the engine
    engine = VoiceProcessingEngine(
        model=Gpt41Mini(Providers.OPENAI),
        system_prompt=SYSTEM_PROMPT,
        session_id="test",
    )

    # Register cli components
    cli = VoiceProcessingEngineCLI("voice processing engine")
    cli.register_engine(engine)
    cli.register_engine_command(VoiceProcessingEngineCommand, engine.handle_command)
    cli.register_engine_result_component(EngineResultComponent)
    cli.register_loading_event(VoiceProcessingEngineStatusEvent)
    cli.register_component_event(VoiceProcessingEngineToolResultEvent, ToolComponent)
    cli.register_prompt_command(SpecificPromptCommand, SpecificPrompt)
    cli.register_component_event(SpecificComponentEvent, SpecificComponent)

    # Register tools
    await engine.register_tool(merge_speakers)

    await cli.main()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())


