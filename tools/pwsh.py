from typing import Optional
import subprocess
import os
from loguru import logger
from src.framework.tool_calling import openai_function_wrapper

@openai_function_wrapper(
    funct_descript="Execute a PowerShell command",
    param_descript={
        "command": "The PowerShell command to execute",
    }
)
def execute_command(
        command: str,
        working_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))),
        timeout: int = 30
) -> str:
    """Execute a PowerShell command and return the stdout output"""
    try:
        # Store original directory if we need to change
        original_dir = os.getcwd() if working_dir else None

        # Change directory if specified
        if working_dir:
            os.chdir(working_dir)
            logger.debug(f"Changed to directory: {working_dir}")

        try:
            # Execute PowerShell command with proper encoding
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                encoding='utf-8',  # Specify UTF-8 encoding
                errors='replace',  # Replace invalid characters
                timeout=timeout,
                startupinfo=startupinfo,
                env=dict(os.environ, PYTHONIOENCODING='utf-8')  # Ensure Python uses UTF-8
            )

            # Check for errors
            if process.returncode != 0:
                error_msg = process.stderr.strip() if process.stderr else "Unknown error"
                raise ValueError(f"Command failed: {error_msg}")

            output = process.stdout.strip()
            # Clean the output by removing ANSI escape codes if present
            # try:
            #     import re
            #     ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            #     output = ansi_escape.sub('', output)
            # except:
            #     pass

            return output

        finally:
            # Restore original directory if we changed it
            if original_dir:
                os.chdir(original_dir)
                logger.debug(f"Restored original directory: {original_dir}")

    except subprocess.TimeoutExpired:
        raise ValueError(f"Command timed out after {timeout} seconds")
    except Exception as e:
        raise ValueError(f"Error executing command: {str(e)}")
