"""Tools for the AI CLI assistant."""

import ast
import json
import os
import re
import random
from typing import Any, Dict, List
from pathlib import Path
from openai.types.chat import ChatCompletionToolParam


class Calculator:
    """Mathematical expression calculator tool."""
    
    name = "calculator"
    description = "Evaluate mathematical expressions safely"
    
    def get_schema(self) -> ChatCompletionToolParam:
        """Get the OpenAI function schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    
    async def execute(self, expression: str) -> str:
        """Execute the calculator tool."""
        try:
            clean_expr = self._clean_expression(expression)
            if not self._is_safe_expression(clean_expr):
                return "Error: Expression contains unsafe operations or characters."
            
            result = eval(clean_expr, {"__builtins__": {}}, {})
            
            return f"Result: {result}"
            
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    def _clean_expression(self, expression: str) -> str:
        """Clean the expression string."""
        cleaned = re.sub(r'\s+', '', expression)
        cleaned = cleaned.replace('x', '*').replace('÷', '/').replace('-', '-')
        return cleaned
    
    def _is_safe_expression(self, expression: str) -> bool:
        """Check if the expression is safe to evaluate."""
        safe_pattern = r'^[\d\+\-\*\/\(\)\.\s]+$'
        return bool(re.match(safe_pattern, expression))


class WebSearch:
    """Web search tool using OpenAI API with web search."""
    
    name = "web_search"
    description = "Search the web for current information using OpenAI's web search"
    
    def __init__(self, config):
        """Initialize with configuration."""
        self.config = config
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.config.openai_api_key)
        except ImportError:
            raise ImportError("OpenAI library is required for web search functionality")
    
    def get_schema(self) -> ChatCompletionToolParam:
        """Get the OpenAI function schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query to look up on the web"
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    async def execute(self, query: str) -> str:
        """Execute the web search tool using OpenAI API."""
        try:
            if not self.client:
                return "Error: OpenAI client not initialized. Please check your API key configuration."
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": f"Search the web for current information about: {query}. Provide a comprehensive summary with relevant details and sources."
                    }
                ],
                **self.config.to_dict()
            )
            
            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return f"🌐 Web Search Results for '{query}':\n\n{content}"
            else:
                return f"Error: No response received from web search for '{query}'"
                
        except Exception as e:
            return f"Error performing web search: {str(e)}\n\nNote: Make sure your OpenAI API key is valid and you have access to web search capabilities."


class SlotMachine:
    """Slot machine gambling game tool."""
    
    name = "slot_machine"
    description = "Play a virtual slot machine game with virtual credits"
    
    def __init__(self):
        self.symbols = ["🍒", "🍇", "💎", "7️⃣", "🎰", "⭐"]
        self.payouts = {
            "🍒": 10,   
            "🍇": 20,   
            "💎": 50,   
            "7️⃣": 100,  
            "🎰": 200,  
            "⭐": 500   
        }
        self.player_credits = 1000  # Starting credits
    
    def get_schema(self) -> ChatCompletionToolParam:
        """Get the OpenAI function schema for this tool."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["spin", "balance", "help"],
                            "description": "Action to perform: spin (play), balance (check credits), help (show rules)"
                        },
                        "bet_amount": {
                            "type": "integer",
                            "description": "Amount to bet (1-100 credits, only used with spin action)"
                        }
                    },
                    "required": ["action"]
                }
            }
        }
    
    async def execute(self, action: str, bet_amount: int = 10) -> str:
        """Execute the slot machine tool."""
        try:
            if action == "spin":
                return await self._spin(bet_amount)
            elif action == "balance":
                return await self._check_balance()
            elif action == "help":
                return await self._show_help()
            else:
                return f"Unknown action: {action}. Use 'help' to see available actions."
                
        except Exception as e:
            return f"Error in slot machine: {str(e)}"
    
    async def _spin(self, bet_amount: int) -> str:
        """Spin the slot machine."""
        if bet_amount < 1 or bet_amount > 100:
            return "Bet amount must be between 1 and 100 credits."
        
        if bet_amount > self.player_credits:
            return f"Insufficient credits! You have {self.player_credits} credits, but want to bet {bet_amount}."
        
        self.player_credits -= bet_amount

        reels = [random.choice(self.symbols) for _ in range(3)]
        
        winnings = self._calculate_winnings(reels, bet_amount)
        self.player_credits += winnings
        
        slot_display = f"[ {' | '.join(reels)} ]"
        
        result = f"🎰 SLOT MACHINE SPIN 🎰\n\n"
        result += f"Reels: {slot_display}\n"
        result += f"Bet: {bet_amount} credits\n"
        
        if winnings > 0:
            result += f"🎉 WIN! You won {winnings} credits! 🎉\n"
        else:
            result += f"😔 No win this time...\n"
        
        result += f"Current balance: {self.player_credits} credits"
        
        return result
    
    async def _check_balance(self) -> str:
        """Check current credit balance."""
        return f"💰 Current balance: {self.player_credits} credits"
    
    async def _show_help(self) -> str:
        """Show slot machine rules and payouts."""
        help_text = "🎰 SLOT MACHINE RULES 🎰\n\n"
        help_text += "Actions:\n"
        help_text += "• spin - Play the slot machine\n"
        help_text += "• balance - Check your credit balance\n"
        help_text += "• help - Show this help message\n\n"
        help_text += "Payouts (per credit bet):\n"
        
        for symbol, payout in self.payouts.items():
            help_text += f"• {symbol} = {payout} credits\n"
        
        help_text += "\nSpecial Combinations:\n"
        help_text += "• Three matching symbols = payout × bet amount\n"
        help_text += "• Three 7️⃣ = 1000 credits (Mega Jackpot!)\n"
        help_text += "• Three 🎰 = 5000 credits (Super Jackpot!)\n"
        help_text += "• Three ⭐ = 10000 credits (Ultimate Jackpot!)\n\n"
        help_text += f"Starting balance: 1000 credits\n"
        help_text += f"Current balance: {self.player_credits} credits"
        
        return help_text
    
    def _calculate_winnings(self, reels: List[str], bet_amount: int) -> int:
        """Calculate winnings based on the reels."""
        # Check if all three symbols match
        if len(set(reels)) == 1:
            symbol = reels[0]
            base_payout = self.payouts.get(symbol, 0)
            
            # Special jackpot combinations
            if symbol == "7️⃣":
                return 1000
            elif symbol == "🎰":
                return 5000
            elif symbol == "⭐":
                return 10000
            else:
                return base_payout * bet_amount
        
        return 0  # No win