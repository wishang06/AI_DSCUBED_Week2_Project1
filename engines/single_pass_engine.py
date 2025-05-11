from dataclasses import dataclass
from typing import Optional
import uuid
from llmgine.llm.engine.engine import Engine
from llmgine.llm.models.model import Model
from llmgine.messages.commands import Command, CommandResult
from llmgine.bus.bus import MessageBus
from llmgine.messages.events import Event

@dataclass
class SinglePassEngineCommand(Command):
    prompt: str = ""

@dataclass
class SinglePassEngineStatusEvent(Event):
    status: str = ""


class SinglePassEngine(Engine):

    def __init__(
          self,
          model: Model, 
          system_prompt: Optional[str] = None, 
          session_id: Optional[str] = None
    ) :

        self.model = model
        self.system_prompt = system_prompt
        self.session_id = session_id
        self.bus = MessageBus()

    async def handle_command(self, command: SinglePassEngineCommand) -> CommandResult:
        try:
            result = await self.execute(command.prompt)
            return CommandResult(success=True, result=result)
        except Exception as e:
            return CommandResult(success=False, error=str(e))
        

    async def execute(self, prompt: str) -> str:
        if self.system_prompt:
            context = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ]
        else:
            context = [{"role": "user", "content": prompt}]
        await self.bus.publish(
            SinglePassEngineStatusEvent(status="Calling LLM", session_id=self.session_id)
        )
        response = await self.model.generate(context)
        await self.bus.publish(
            SinglePassEngineStatusEvent(status="finished", session_id=self.session_id)
        )
        return response.content


async def use_single_pass_engine(
    prompt: str, model: Model, system_prompt: Optional[str] = None
):

    session_id = str(uuid.uuid4())
    engine = SinglePassEngine(model, system_prompt, session_id)
    return await engine.execute(prompt)


async def main(case: int):
    from llmgine.ui.cli.cli import EngineCLI
    from llmgine.ui.cli.components import EngineResultComponent
    from llmgine.bootstrap import ApplicationConfig, ApplicationBootstrap
    from llmgine.llm.models.openai_models import Gpt41Mini
    from llmgine.llm.providers.providers import Providers

    config = ApplicationConfig(enable_console_handler=False)
    bootstrap = ApplicationBootstrap(config)
    await bootstrap.bootstrap()
    if case == 1:
        engine = SinglePassEngine(
            Gpt41Mini(Providers.OPENAI), "respond in pirate", "test"
        )
        cli = EngineCLI("test")
        cli.register_engine(engine)
        cli.register_engine_command(SinglePassEngineCommand, engine.handle_command)
        cli.register_engine_result_component(EngineResultComponent)
        cli.register_loading_event(SinglePassEngineStatusEvent)
        await cli.main()
    elif case == 2:
        result = await use_single_pass_engine(
            "Hello, world!", Gpt41Mini(Providers.OPENAI), "respond in pirate"
        )
        print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main(1))

