from openai import OpenAI
from pprint import pprint

client = OpenAI(api_key="sk-97ebe7316d0e4862a6cc33ce7000b9f4", base_url="https://api.deepseek.com")

import os
from tools.test import weather
from src.framework.tool_calling.tool_calling import ToolManager
from src.framework.core.store import ContextStore
from src.framework.core.observer import DummieEngineSubject
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich import print
from rich.console import Group
from rich.rule import Rule
from src.framework.clients.response import StreamedResponseWrapperOpenAI
from src.framework.types.clients import OpenAIReasoningAPIFormat

context_store = ContextStore("You are a helpful assistant")

context_store.store_string("tell me about short-term memory", "user")

response = StreamedResponseWrapperOpenAI(client.chat.completions.create(
    model="deepseek-reasoner",
    messages=context_store.retrieve(),
    stream=True,
    stream_options={"include_usage": True}
), OpenAIReasoningAPIFormat.DEEPSEEK)

for chunk in response:
    os.system('cls' if os.name == 'nt' else 'clear')
    print(response.reasoning if response.reasoning else "")
    if response.content:
        print("================================")
        print(response.content)
    else:
        continue

# streamed_response = {
#     "reasoning_content": "",
#     "content": "",
#     "usage": None,
#     "chunks": []
# }
#
# print(Panel(Text("Streaming response from DeepSeek", style="blue", justify="center"), style="blue"))
#
# with Live(Panel(""), vertical_overflow='visible', auto_refresh=True) as live:
#     for chunk in response:
#         if chunk.choices[0].delta.content:
#             streamed_response['content'] += chunk.choices[0].delta.content
#             live.update(Panel(Group(
#                 Rule('Reasoning'),
#                 Markdown(streamed_response['reasoning_content']),
#                 Rule('Content'),
#                 Markdown(streamed_response['content']
#                          ))))
#         if chunk.choices[0].delta.reasoning_content:
#             streamed_response['reasoning_content'] += chunk.choices[0].delta.reasoning_content
#             live.update(
#                 Panel(Group(Rule("Reasoning"), Markdown(streamed_response['reasoning_content']))))
#         streamed_response['chunks'].append(chunk)
#
# print(response)
# print("====" * 10)
# print(response.reasoning)
# print("====" * 10)
# print(response.content)
