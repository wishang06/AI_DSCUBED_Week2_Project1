import os
from typing import List
from framework.tool_calling import openai_function_wrapper
from loguru import logger

class TerminalOperations:
    """File operations tool for basic file management"""
    def __init__(self, current_directory: str = "."):
        # Set the initial current directory and change the working directory
        self.set_current_directory(current_directory)

    """File operations tool for basic file management"""

    def set_current_directory(self, path: str) -> None:
        """Set the current working directory for the entire process."""
        logger.info(f"Setting current directory to: {path}")
        try:
            # Resolve the absolute path
            resolved_path = os.path.abspath(path)
            if not os.path.isdir(resolved_path):
                raise ValueError(f"Invalid directory: {resolved_path}")
            # Change the current working directory
            os.chdir(resolved_path)
            self.current_directory = resolved_path
        except Exception as e:
            raise ValueError(f"Error setting current directory: {str(e)}")
    
    @staticmethod
    @openai_function_wrapper(
        funct_descript="List contents of a directory",
        param_descript={
            "path": "Directory path to list contents from"
        }
    )
    def list_directory(path: str = ".") -> List[str]:
        logger.debug(f"Listing directory: {path}")
        """List contents of a directory"""
        try:
            return os.listdir(path)
        except Exception as e:
            raise ValueError(f"Error listing directory: {str(e)}")
    
    @staticmethod
    @openai_function_wrapper(
        funct_descript="Read contents of a file",
        param_descript={
            "path": "Path to the file to read",
            "max_size": "Maximum file size in bytes (default 1MB)"
        }
    )
    def read_file(path: str, max_size: int = 1024 * 1024) -> str:
        """Read contents of a file"""
        logger.debug(f"Reading file: {path}")
        try:
            if not os.path.exists(path):
                raise ValueError(f"File not found: {path}")
            
            file_size = os.path.getsize(path)
            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes (max {max_size} bytes)")
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    @staticmethod
    @openai_function_wrapper(
        funct_descript="Write content to a file",
        param_descript={
            "path": "Path where to write the file",
            "content": "Content to write to the file",
            "overwrite": "Whether to overwrite if file exists"
        }
    )
    def write_file(path: str, content: str, overwrite: bool = False):
        """Write content to a file"""
        logger.debug(f"Writing file: {path}, overwrite: {overwrite}\nContent: {content}")
        try:
            if os.path.exists(path) and not overwrite:
                raise ValueError(f"File already exists: {path}")
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content) if content else f.write("")
            return "File written successfully"
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")
    
    @staticmethod
    @openai_function_wrapper(
        funct_descript="Delete a file",
        param_descript={
            "path": "Path to the file to delete"
        }
    )
    def delete_file(path: str):
        """Delete a file"""
        logger.debug(f"Deleting file: {path}")
        try:
            if not os.path.exists(path):
                raise ValueError(f"File not found: {path}")
            
            os.remove(path)
            return "File deleted successfully"
        except Exception as e:
            raise ValueError(f"Error deleting file: {str(e)}")
    
    @staticmethod
    @openai_function_wrapper(
        funct_descript="Create a new directory",
        param_descript={
            "path": "Path where to create the directory"
        }
    )
    def create_directory(path: str):
        """Create a directory"""
        logger.debug(f"Creating directory: {path}")
        try:
            if os.path.exists(path):
                raise ValueError(f"Directory already exists: {path}")
            
            os.makedirs(path)
            return "Directory created successfully"
        except Exception as e:
            raise ValueError(f"Error creating directory: {str(e)}")

    # @staticmethod
    # @openai_function_wrapper(
    #     funct_descript="Execute any PowerShell command and returns the command output (stdout)",
    #     param_descript={
    #         "command": "The PowerShell command to execute",
    #         "timeout": "Maximum execution time in seconds"
    #     }
    # )
    # def execute_command(command: str, timeout: int = 30) -> str:
    #     """Execute a PowerShell command and return the stdout output
    #
    #     Args:
    #         command: The PowerShell command to execute
    #         timeout: Maximum execution time in seconds (default 30)
    #
    #     Returns:
    #         str: Standard output from the command execution
    #
    #     Raises:
    #         ValueError: If command execution fails
    #     """
    #     logger.debug(f"Executing PowerShell command: {command}")
    #     try:
    #         import subprocess
    #
    #         # Execute PowerShell command with timeout
    #         process = subprocess.run(
    #             ["powershell", "-Command", command],
    #             capture_output=True,
    #             text=True,
    #             timeout=timeout
    #         )
    #
    #         if process.returncode != 0:
    #             raise ValueError(f"Command failed: {process.stderr} {process.stdout}")
    #
    #         return process.stdout.strip()
    #
    #     except subprocess.TimeoutExpired:
    #         raise ValueError(f"Command timed out after {timeout} seconds")
    #     except subprocess.SubprocessError as e:
    #         raise ValueError(f"Error executing command: {str(e)}")
    #     except Exception as e:
    #         raise ValueError(f"Unexpected error: {str(e)}")
