from rich import print
from rich.pretty import Pretty, pprint
from rich.panel import Panel
from rich.console import Console

data = {
    'data': 'value',
    'nested': {
        'key': 'value',
        'list': [1, 2, 3],
    },
}


console = Console()
console.print(Panel(Pretty(data, expand_all=True), title="Data"))
