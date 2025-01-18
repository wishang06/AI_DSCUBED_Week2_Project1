import dotenv
import json
import os
from src.framework.clients import ClientOpenAI

FILE_PATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(FILE_PATH)

def get_file_path(filename):
    return os.path.join(SCRIPT_DIR, filename)

def dump_to_file(variable, name):
    output_file = get_file_path(f"{name}.json")
    json.dump(json.loads(variable.to_json()), open(output_file, "w"), indent=4)

def main():
    # normal openai
    dotenv.load_dotenv()
    openai_client = ClientOpenAI.create_openai(os.getenv("OPENAI_API_KEY"))
    openai_response_generic = openai_client.create_completion("gpt-4o-mini",
        context = [{"role": "user", "content": "Does the black moon howl?"}])
    dump_to_file(openai_response_generic.full, "openai_response_generic")
    # openai with tool call
    openai_response_tool_call = openai_client.create_tool_completion("gpt-4o-mini",
        context = [{"role": "user", "content": "What is the weather in San Francisco?"}],
        tools = [{
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the weather in a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city to get the weather for"
                        }
                    },
                    "required": ["city"]
                }
            }
        }])
    dump_to_file(openai_response_tool_call.full, "openai_response_tool_call")



if __name__ == "__main__":
    main()
