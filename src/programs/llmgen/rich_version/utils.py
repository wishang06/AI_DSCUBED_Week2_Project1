# other random functions go here
from typing import Optional, Dict, Any
import json
from pathlib import Path


def load_json_file(path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise ValueError(f"Error loading JSON file {path}: {str(e)}")


def save_json_file(data: Dict[str, Any], path: Path) -> None:
    """Save data to a JSON file"""
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise ValueError(f"Error saving JSON file {path}: {str(e)}")


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values"""
    return {
        "mode": "normal",
        "model_name": "gpt-4o-mini",
        "system_prompt_path": "prompts/core/agents/system.md"
    }


def format_command_help() -> str:
    """Format help text for available commands"""
    return """
Available Commands:
------------------
/exit - Exit the program
/clear - Clear chat history
/help - Show this help menu
/model <name> - Switch to a different model
/mode <mode> - Change engine mode (normal, minimal, chain, linear_chain)
/system <path> - Load new system prompt from file
/tools - List available tools
/history - Show chat history
/export [path] - Export chat history to JSON (default: chat_history.json)
/load <path> - Load chat history from JSON file
"""
