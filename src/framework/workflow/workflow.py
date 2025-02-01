from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from enum import Enum, auto
from traceback import format_exc
from loguru import logger

# Type variables for generic type hints
T = TypeVar('T')


class BlockState(Enum):
    """State management for blocks"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()


class BlockExecutionMessage(Enum):
    """Block execution result messages"""
    ERROR = auto()
    SUCCESS = auto()
    END_WORKFLOW = auto()


@dataclass
class WorkflowResult:
    """Result object to pass between blocks"""
    name: str
    value: Any
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"Result(name={self.name}, value={self.value})"


@dataclass
class BlockExecutionResult:
    """Comprehensive result of block execution"""
    block: Block
    message: BlockExecutionMessage
    result: Optional[WorkflowResult] = None
    error: Optional[Exception] = None
    traceback: Optional[str] = None


@dataclass
class WorkflowContext:
    """Maintains workflow context with history"""
    history: List[Dict[str, Any]] = field(default_factory=list)

    def update(self, key: str, value: Any):
        """Update context with new value and maintain history"""
        self.history.append({key: value})




class WorkflowSubject:
    """Subject class for workflow observers"""

    def __init__(self):
        self.observers: List['WorkflowObserver'] = []

    def attach(self, observer: 'WorkflowObserver'):
        """Attach an observer to the subject"""
        self.observers.append(observer)

    def detach(self, observer: 'WorkflowObserver'):
        """Detach an observer from the subject"""
        self.observers.remove(observer)

    def notify(self, message: str):
        """Notify all observers with a message"""
        for observer in self.observers:
            observer.update(message)

class WorkflowObserver:
    """Observer class for workflow notifications"""

    def update(self, message: str):
        """Update method for observers"""
        raise NotImplementedError("Update method must be implemented in subclass")


class Workflow:
    """Main workflow class"""

    def __init__(self):
        self.blocks: Dict[str, Block] = {}
        self.start: Optional[Block] = None
        self.context = WorkflowContext()
        self.queue: List[str] = []
        self.current_block: Optional[Block] = None
        self.final_result: Optional[WorkflowResult] = None
        self.subject = WorkflowSubject()

    def __getitem__(self, key: str) -> Block:
        """Get a block by name"""
        if key not in self.blocks:
            raise KeyError(f"Block {key} not found in workflow")
        return self.blocks[key]

    def __setitem__(self, key: str, value: Block):
        """Set a block by name"""
        self.blocks[key] = value

    def add_block(self, block: Block) -> Block:
        """Add a block to the workflow"""
        block.workflow_subject = self.subject
        self.blocks[block.name] = block
        return block

    def queue_block(self, block_name: str):
        """Queue a block for execution"""
        if block_name not in self.blocks:
            raise ValueError(f"Block {block_name} not found")
        self.queue.append(block_name)

    def reset(self):
        """Reset the entire workflow state"""
        self.context = WorkflowContext()
        self.queue = []
        self.current_block = None
        self.final_result = None
        for block in self.blocks.values():
            block.reset()

    def validate(self) -> bool:
        """Validate workflow configuration"""
        if not self.start:
            raise ValueError("No start block defined")
        if not self.blocks:
            raise ValueError("No blocks defined in workflow")
        return True

    def run(self) -> Optional[WorkflowResult]:
        """Execute the workflow"""
        try:
            self.validate()
            logger.info(f"Starting workflow execution from block: {self.start.name}")

            # Execute start block
            result = self._run_block(self.start)
            if result.message == BlockExecutionMessage.ERROR:
                raise BlockException(
                    f"Start block {self.start.name} failed",
                    self.start,
                    result.traceback
                )

            # Update context with start block result
            self.context.update(self.start.name, result.result.value)

            # Process queue until empty or workflow ends
            while self.queue:
                next_block_name = self.queue.pop(0)
                block = self.blocks[next_block_name]
                result = self._run_block(block)
                self.context.update(block.name, result.result.value)

                if result.message == BlockExecutionMessage.END_WORKFLOW:
                    logger.info(f"Workflow completed at exit block: {block.name}")
                    return result.result

                elif result.message == BlockExecutionMessage.ERROR:
                    raise BlockException(
                        f"Block {block.name} failed",
                        block,
                        result.traceback
                    )

            logger.warning("Workflow completed without reaching exit block")
            return None

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            raise

    def _run_block(self, block: Block) -> BlockExecutionResult:
        """Execute a single block and handle its result"""
        logger.debug(f"Executing block: {block.name}")
        self.current_block = block

        # Handle exit blocks
        if block.is_exit:
            result = block.run(self)
            if result.message == BlockExecutionMessage.SUCCESS:
                self.final_result = result.result
                result.message = BlockExecutionMessage.END_WORKFLOW
            return result

        # Execute block
        result = block.run(self)
        if result.message != BlockExecutionMessage.SUCCESS:
            return result

        # Handle next blocks based on result
        if isinstance(block, BinaryDecision):
            next_block = block.next_blocks.get(result.result.value)
        else:
            next_block = block.next_blocks.get("default")

        if next_block:
            self.queue_block(next_block.name)
        else:
            logger.warning(f"No next block found for {block.name}")

        return result

    def get_block_status(self) -> Dict[str, BlockState]:
        """Get the current state of all blocks"""
        return {name: block.state for name, block in self.blocks.items()}

    def get_execution_path(self) -> List[str]:
        """Get the list of executed blocks in order"""
        # todo: implement this method
        return ["hello"]
