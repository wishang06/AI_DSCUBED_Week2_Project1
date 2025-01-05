import anthropic
from .response import ResponseWrapperAnthropic

class ClientAnthropic:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)

    def convert_to_anthorpic(self, context):
        if context == None:
            return [], None
        elif context[0]["role"] == "system":
            return context[1:], context[0].content
        else:
            return context, None
    

    def create_completion(self, model_name, context):
        context, system = self.convert_to_anthorpic(context)
        system = system or ""
        response = self.client.messages.create(model=model_name,
                                                   system=system, 
                                                   messages=context,
                                                   temperature=1,
                                                   max_tokens=8000)
        return ResponseWrapperAnthropic(response)