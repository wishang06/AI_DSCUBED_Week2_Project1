from src.framework.types import Block
from typing import Any, Callable, Dict, Optional, Union

class FunctionBlock:
    """Block class representing a node in the workflow"""

    def __init__(
            self,
            name: str,
            function: Optional[Callable] = None,
            engine: Optional[Any] = None,
            prompt: Optional[str] = None,
            is_exit: bool = False,
    ):
        self.name = name
        self.function = function
        self.engine = engine
        self.prompt = prompt
        self.is_exit = is_exit
        self.next_blocks: Dict[str, 'Block'] = {}
        self.state = BlockState.PENDING
        self.result: Optional[Result] = None
        self.parent: Optional['Block'] = None
        self.workflow_subject = None

    def add(self, name_or_block: Union[str, 'Block', 'BinaryDecision'],
            engine: Optional[Any] = None,
            prompt: Optional[str] = None,
            condition: str = "default") -> 'Block':
        """Add a next block with an optional condition"""
        if isinstance(name_or_block, str):
            block = Block(name_or_block, engine=engine, prompt=prompt)
        else:
            block = name_or_block

        block.parent = self
        self.next_blocks[condition] = block
        return block

    def reset(self):
        """Reset block state"""
        self.state = BlockState.PENDING
        self.result = None

    def run(self, workflow: 'Workflow') -> BlockExecutionResult:
        """Execute the block's logic"""
        self.state = BlockState.RUNNING
        try:
            self.workflow_subject.notify(f"Running block: {self.name}")
            # Execute the appropriate type of content
            if self.function:
                result = self.function(workflow)
                self.result = Result(self.name, result)
            elif self.engine and self.prompt:
                context = workflow.context.history
                context_str = f" with context: {context}" if context else ""
                self.workflow_subject.notify(f"Executing block {self.name}{context_str}")
                result = self.engine.execute(self.prompt + context_str)
                self.result = Result(self.name, result)
            else:
                raise ValueError(f"Block {self.name} has no executable content")

            self.state = BlockState.COMPLETED
            self.workflow_subject.notify(f"Block {self.name} completed with result: {self.result}")
            return BlockExecutionResult(
                block=self,
                message=BlockExecutionMessage.SUCCESS,
                result=self.result
            )

        except Exception as e:
            self.state = BlockState.FAILED
            return BlockExecutionResult(
                block=self,
                message=BlockExecutionMessage.ERROR,
                error=e,
                traceback=format_exc()
            )


class PromptBlock


class BinaryDecision(Block):
    """Decision block for conditional branching"""

    def __init__(
            self,
            name: str,
            function: Callable[[Any], bool],
            true_path: str = "yes",
            false_path: str = "no"
    ):
        super().__init__(name, function)
        self.true_path = true_path
        self.false_path = false_path

    def run(self, workflow: 'Workflow') -> BlockExecutionResult:
        """Execute decision logic"""
        result = super().run(workflow)
        if result.message == BlockExecutionMessage.SUCCESS:
            # Convert result to boolean and set appropriate path
            path = self.true_path if result.result.value else self.false_path
            result.result.value = path
            return result
        if result.message == BlockExecutionMessage.ERROR:
            raise BlockException(
                f"Decision block {self.name} failed",
                self,
                result.traceback
            )
