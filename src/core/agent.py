from src.tool_calling.tool_calling import (
    openai_function_wrapper,
    create_tools_schema,
    create_tools_lookup,
    execute_function
)
from src.types.model_config import LLMInit
from src.utils.callbacks import CLICallback
from src.core.engine import AgentEngine
from src.types.callbacks import Callback



class BasicAgent():
    def __init__(self, config: LLMInit, callback: Callback):
        """_summary_

        Args:
            config (LLMInit): _description_
            callback (Callback): _description_
        """
        self.callback = callback 
        self.config = config
        self.engine = AgentEngine(
            client=config.client,
            model_name=config.model_name,
            system_prompt=config.system_prompt,
            tools=config.tools,
            callback=callback
        )

    def self_tools(self):
        # 1
        @openai_function_wrapper(
            function_description="Add an prompt to your own the prompt queue.",
            parameter_descriptions={
                "prompt": "prompt in string format"}
        )
        def self_prompt(prompt: str) -> str:
            self.queue_prompt("(self-prompted) " + prompt)
            return f"Prompt added to queue: {prompt}"
        self.add_agent_tools(self_prompt)
        # 2
        @openai_function_wrapper(
            function_description="There's enough information about the \
                requirement of the task. By executing this function, \
                you will proceed to the plannig step.",
            parameter_descriptions={}
        )
        def finish_task_definition():
            self.engine.state = "planning"
            return "Task definition finished."
        # 3
        @openai_function_wrapper(
            function_description="The user has approved your plan. \
                By executing this function, you will proceed to\
                the exeuction step.",
            parameter_descriptions={}
        )
        def finish_planning():
            self.engine.state = "execution"
            return "Planning finished."
        # 4
        @openai_function_wrapper(
            function_description="You need help/additional input/approval from the user. \
                By executing this function, you will proceed to the \
                user input step.",
            parameter_descriptions={}
        )
        def get_user_input():
            self.engine.state = "user_input"
            return "User input started."
        # 5
        @openai_function_wrapper(
            function_description="The user has provided the required input. \
                By executing this function, you will proceed back to the  \
                execution step.",
            parameter_descriptions={}
        )
        def finish_user_input():
            self.engine.state = "execution"
            return "User input finished."
