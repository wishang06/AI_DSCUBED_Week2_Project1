from src.framework.types.callbacks import StatusCallback, SimpleCallback

class DummieStatusCallback(StatusCallback):
    def execute(self, message: str) -> None:
        pass
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def update_status(self, message: str) -> None:
        pass

    def get_input(self, message: str) -> str:
        return ""

class CLIStatusCallback(StatusCallback):
    def __init__(self, cli):
        self.cli = cli
        self.loading = None
        
    def execute(self, message: str, title: str, style: str) -> None:
        self.cli.print_message(message, title, style)
    
    def __enter__(self):
        self.loading = self.cli.show_loading("Engine starting...").__enter__()
        return self.loading
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.loading:
            self.loading.__exit__(exc_type, exc_val, exc_tb)
            self.loading = None
    
    def update_status(self, message: str) -> None:
        if self.loading:
            self.loading.update_status(message)
    
    def get_input(self, message: str) -> str:
        return self.cli.get_input(message)

class FunctionStudioSimpleCallback(SimpleCallback):
    def __init__(self):
        self.data = {}

    def do(self, key: str, data: str):
        self.data[key] = data
