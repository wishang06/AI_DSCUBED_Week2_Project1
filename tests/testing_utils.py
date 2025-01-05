from openai.types.chat import ChatCompletion
from anthropic.types import Message

def read_json_file(file_path):
    with open(file_path, "r") as file:
        return file.read()
    
def read_openai_response(file_path):
    temp = read_json_file(file_path)
    return ChatCompletion.model_validate_json(temp)

def read_anthropic_response(file_path):
    temp = read_json_file(file_path)
    return Message.model_validate_json(temp)
    
def local():
    openai_response_generic = read_openai_response("tests/test_responses_objects/openai_response.json")
    print(openai_response_generic)
    anthropic_response_generic = read_anthropic_response("tests/test_responses_objects/anthropic_response_generic.json")
    print(anthropic_response_generic)

if __name__ == "__main__":
    local()