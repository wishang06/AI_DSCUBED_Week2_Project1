# cost.py

import sys

def calculate_cost(model, input_tokens, output_tokens) -> float:
    """
    Calculate the cost of running the model based on input and output tokens,
    with pricing defined per 1 million tokens.

    Args:
        model (str): The name of the model being used.
        input_tokens (int): Number of input tokens.
        output_tokens (int): Number of output tokens.

    Returns:
        float: The total cost of running the model.
    """
    # Example pricing scheme per 1 million tokens (modify as needed)
    pricing = {
        "1": {"input_cost_per_million": 2.5, "output_cost_per_million": 10}, #gpt4o
        "2": {"input_cost_per_million": 3, "output_cost_per_million": 15}, #claude 3.5 sonnet
        "3": {"input_cost_per_million": 1.25, "output_cost_per_million": 5} #gemini
    }
    
    if model not in pricing:
        raise ValueError(f"Pricing for model '{model}' is not defined.")

    input_cost_per_million = pricing[model]["input_cost_per_million"]
    output_cost_per_million = pricing[model]["output_cost_per_million"]

    # Calculate costs based on token counts (convert to millions)
    total_cost = ((input_tokens / 1_000_000) * input_cost_per_million) + \
                 ((output_tokens / 1_000_000) * output_cost_per_million)
    return total_cost

if __name__ == "__main__":
    # Ensure there are enough command-line arguments
    if len(sys.argv) != 4:
        print("Usage: python cost.py <model> <input_tokens> <output_tokens>")
        sys.exit(1)

    # Parse command-line arguments
    model = sys.argv[1]
    try:
        input_tokens = int(sys.argv[2])
        output_tokens = int(sys.argv[3])
    except ValueError:
        print("Error: input_tokens and output_tokens must be integers.")
        sys.exit(1)

    # Calculate cost
    try:
        cost = calculate_cost(model, input_tokens, output_tokens)
        print(f"Total cost for running the model: ${cost:.4f}")
    except ValueError as e:
        print(e)
        sys.exit(1)
