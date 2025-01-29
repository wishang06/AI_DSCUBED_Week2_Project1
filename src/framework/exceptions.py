class ResponseConversionError(Exception):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


class WorkflowError(Exception):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response

class BlockError(Exception):
    def __init__(self, message, response):
        super().__init__(message)
        self.response = response


class BlockException(Exception):
    """Custom exception for block execution failures"""

    def __init__(self, message: str, block: Block, traceback: Optional[str] = None):
        super().__init__(message)
        self.block = block
        self.traceback = traceback or format_exc()
