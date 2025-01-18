from src.framework.prompts import Prompt
from src.framework.tool_calling import openai_function_wrapper
import json

@openai_function_wrapper(function_description="Create a proper reusable \
                         customizable prompt with a name, prompt, and arguments",
                         parameter_descriptions={
                             "name": "Name of the prompt, in snake_case",
                             "prompt": r"Prompt string with format placeholders \
                                for arguments using Python string formatting { }",
                             "args": r"Dictionary of argument names and descriptions \
                                format {'arg_name': 'arg_description', \
                                        'arg_name2': 'arg_description2'}",
                             "save": "Whether to save the prompt to a file"})
def make_prompt(name: str, prompt: str, args, save=False) -> Prompt:
    args = json.loads(args.replace("'", '"'))
    if save:
        with open(f"prompts/{name}.json", 'w') as file:
            json.dump({'args': args, 'prompt': prompt}, file, indent=4)
    print(f"Created prompt {name} with prompt: {prompt} and args: {args}")
    return Prompt({'prompt': prompt, 'args': args})

@openai_function_wrapper(function_description="Create an instruction string",
                         parameter_descriptions={
                             "instruction": "Instruction string"})
def create_instruction(instruction: str) -> str:
    return instruction

def go_to_directory(directory: str):
    pass

def list_directory(directory: str):
    pass

def load_and_run_instruction(instruction: str):

    engine.execute_instructions([instruction])

if __name__ == "__main__":
    from src.framework.utils.local_test import setup_test
    client, engine = setup_test()
    engine.add_tool(make_prompt)
    engine.execute_instructions([
        r"Create a prompt called 'hello_world_prompt' with the prompt 'Hello, {name}! Welcome to {place}!' and arguments {name: 'Name of the person', place: 'Place'}, and save it",
    ])
    print(engine.store.retrieve())
