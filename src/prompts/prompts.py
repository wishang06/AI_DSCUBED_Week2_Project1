import json
import re

"""
Prompt Structure
{
"args": {
    "arg1": "description",
    "arg2": "description",
    ...},
"prompt": "prompt string"
}
"""

class Prompt:
    def __init__(self, prompt: dict):
        self.args = prompt['args']
        self.nargs = len(prompt['args'].keys())
        self.prompt = prompt['prompt']
   
    @classmethod
    def from_file(cls, path: str):
        with open(path, 'r') as file:
            prompt = json.load(file)
        return cls(prompt)

    def compile(self, *args) -> str:
        input = {}
        if len(args) != self.nargs:
            raise ValueError(f"Expected {self.nargs} arguments, got {len(args)}")
        i = 0
        for arg in self.args.keys():
            input[arg] = args[i]
            i += 1
        return self.prompt.format(**input)

    @property
    def info(self):
        return f"Prompt has arguments {self.args} and prompt {self.prompt}"

    @property
    def args_info(self):
        return str(self.args)

    def save(self, path: str):
        with open(path, 'w') as file:
            json.dump({'args': self.args, 'prompt': self.prompt}, file, indent=4)

def validate_prompt_format(prompt: str, args: dict[str, str]) -> bool:
    """
    Validates that all args are present in the prompt string as format placeholders.
    
    Args:
        prompt: The prompt string with format placeholders
        args: Dictionary of argument names and descriptions
        
    Returns:
        bool: True if all args are present in prompt, False otherwise
    """
    # Find all format placeholders in prompt
    format_args = sorted(list(set(re.findall(r'\{([^}]+)\}', prompt))))
    # Get sorted list of argument names
    arg_names = sorted(list(args.keys()))
    
    # Check if all args are in format_args and vice versa
    return format_args == arg_names

def make_prompt(name: str, prompt: str, args: dict[str, str], save=False) -> Prompt:
    if save:
        with open(f"prompts/{name}.json", 'w') as file:
            json.dump({'args': args, 'prompt': prompt}, file, indent=4)
    return Prompt({'prompt': prompt, 'args': args})


    
if __name__ == "__main__":
    # Basic prompt testing
    prompt = Prompt.from_file('prompts/hello_world.json')
    print("Basic prompt testing:")
    print(prompt.compile('hello', 'world'))
    print(prompt.info)
    print(prompt.args_info)
    print("=============")
    
    # Testing validate_prompt_format
    print("\nTesting validate_prompt_format:")
    
    def run_test(name: str, prompt: str, args: dict[str, str]):
        # Find format args and arg names for display
        format_args = sorted(list(set(re.findall(r'\{([^}]+)\}', prompt))))
        arg_names = sorted(list(args.keys()))
        is_valid = validate_prompt_format(prompt, args)
        
        print(f"\nTest: {name}")
        print(f"Prompt: {prompt}")
        print(f"Args provided: {args}")
        print(f"Format args found: {format_args}")
        print(f"Arg names provided: {arg_names}")
        print(f"Valid: {is_valid}")
        print("-" * 50)
    
    # Test 1: Valid prompt format
    run_test(
        "Valid format",
        "Test {arg1} and {arg2}",
        {"arg1": "first", "arg2": "second"}
    )
    
    # Test 2: Missing arg in prompt
    run_test(
        "Missing arg in prompt",
        "Test {arg1} only",
        {"arg1": "first", "arg2": "second"}
    )
    
    # Test 3: Extra arg in prompt
    run_test(
        "Extra arg in prompt",
        "Test {arg1} and {arg2} and {arg3}",
        {"arg1": "first", "arg2": "second"}
    )
    
    # Test 4: Empty prompt and args
    run_test(
        "Empty prompt and args",
        "",
        {}
    )
    
    # Test 5: Complex format with multiple occurrences and different order
    run_test(
        "Multiple occurrences and different order",
        "Test {arg2} first, then {arg1} twice: {arg1}",
        {"arg1": "first", "arg2": "second"}
    )
