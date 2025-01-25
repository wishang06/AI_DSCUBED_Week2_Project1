from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum


# State management for blocks
class BlockState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Result object to pass between blocks
@dataclass
class Result:
    name: str
    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


# Block class representing a node in the workflow
class Block:
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

    def run(self, workflow: 'Workflow') -> Result:
        """Execute the block's logic"""
        try:
            self.state = BlockState.RUNNING

            if self.function:
                self.result = self.function(workflow)
            elif self.engine and self.prompt:
                result = self.engine.execute(self.prompt, workflow.context)
                self.result = Result(self.name, result)
            else:
                raise ValueError(f"Block {self.name} has no executable content")

            self.state = BlockState.COMPLETED
            return self.result

        except Exception as e:
            self.state = BlockState.FAILED
            raise WorkflowException(f"Error in block {self.name}: {str(e)}")


# Decision class for conditional branching
class BinaryDecision(Block):
    def __init__(
            self,
            name: str,
            function: Callable,
            true_path: str = "yes",
            false_path: str = "no"
    ):
        super().__init__(name, function)
        self.true_path = true_path
        self.false_path = false_path

    def run(self, workflow: 'Workflow') -> Result:
        result = super().run(workflow)
        # Convert result to boolean or use specified paths
        return Result(self.name,
                      self.true_path if result.value else self.false_path)


class WorkflowException(Exception):
    pass


class Workflow:
    def __init__(self):
        self.blocks: Dict[str, Block] = {}
        self.start: Optional[Block] = None
        self.context: Dict[str, Any] = {}
        self.queue: List[Dict[str, Any]] = []
        self.current_block: Optional[Block] = None

    def __getitem__(self, key: str) -> Block:
        """Get a block by name"""
        if key not in self.blocks:
            raise KeyError(f"Block {key} not found in workflow")
        return self.blocks[key]

    def add_block(self, block: Block) -> Block:
        """Add a block to the workflow"""
        self.blocks[block.name] = block
        return block

    def queue_block(self, block_name: str, context: Dict[str, Any] = None):
        """Queue a block for execution with optional context"""
        self.queue.append({
            "block_name": block_name,
            "context": context or {}
        })

    def llm_decision(self, engine: Any, prompt: str) -> Any:
        """Helper method to make LLM-based decisions"""
        return engine.execute(prompt, self.context)

    def run(self) -> None:
        """Execute the workflow"""
        if not self.start:
            raise WorkflowException("No start block defined")

        try:
            self._run_block(self.start)

            # Process queue until empty
            while self.queue:
                next_item = self.queue.pop(0)
                block = self.blocks[next_item["block_name"]]
                # Update context with queued context
                self.context.update(next_item["context"])
                self._run_block(block)

        except Exception as e:
            raise WorkflowException(f"Workflow execution failed: {str(e)}")

    def _run_block(self, block: Block) -> None:
        """Execute a single block and its subsequent blocks"""
        self.current_block = block

        if block.is_exit:
            result = block.run(self)
            return

        result = block.run(self)

        # Handle next blocks based on result
        next_block = None
        if isinstance(block, BinaryDecision):
            next_block = block.next_blocks.get(result.value)
        else:
            next_block = block.next_blocks.get("default")

        if next_block:
            self._run_block(next_block)


# SimpleEngine implementation
class SimpleEngine:
    def __init__(self, model: str):
        self.model = model

    def execute(self, prompt: str, context: Dict[str, Any]) -> Any:
        """Execute prompt with context"""
        # Implementation would depend on your LLM client
        # This is a placeholder
        return f"Response for {prompt} using {self.model}"
