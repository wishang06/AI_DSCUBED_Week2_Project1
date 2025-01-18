from src.framework.tool_calling import (
    openai_function_wrapper,
    create_tools_schema,
    create_tools_lookup,
    parse_functions,
    execute_function,
)
from src.framework.clients import ClientOpenAI
from src.framework.setup import hello, OPENAI_API_KEY

hello()

@openai_function_wrapper(
    funct_descript="Get the weather for a location",
    param_descript={"location": "The location to get the weather for",
                    "days_from_now": "The number of days from now to get the weather for"},
    required_parameters=["location", "days_from_now"],
    enum_parameters={"location": ["New York", "Los Angeles", "Chicago"]},
)
def get_weather(location: str, days_from_now: int) -> str:
    return f"in {days_from_now}, {location} will be sunny"

tools = [get_weather]
tools_schema = create_tools_schema(tools)
context = [{"role": "system", "content": "You are a helpful assistant."},
           {"role": "user", "content": "What's the weather in New York tomorrow?"}]
client = ClientOpenAI.create_openai(api_key=OPENAI_API_KEY)
response = client.create_tool_completion(model_name="gpt-4o-mini",
                              context=context,
                              tools=tools_schema)

calls = parse_functions(response.tool_calls)
for call in calls:
    result = execute_function(call, tools_lookup=create_tools_lookup(tools))

print("Finished!")