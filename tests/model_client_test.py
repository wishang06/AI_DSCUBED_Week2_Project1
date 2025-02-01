from src.framework.clients.model_manager import set_model, ClientType, ModelRegistry
from src.framework.utils.runtime import get_global_runtime, init_global_runtime
from rich.console import Console
from rich.table import Table
from src.framework.types.clients import ClientType
import os
import dotenv
dotenv.load_dotenv()

def test_client_manager():

    # Initialize runtime
    init_global_runtime()

    # Get all models and their allowed providers from registry
    registry = ModelRegistry()
    test_cases = []

    # Generate all possible model-provider combinations
    for model_name in registry.list_models():
        model_info = registry.get_model_info(model_name)
        # Add case with default provider (None)
        test_cases.append((model_name, None, None))
        # Add cases with each allowed provider
        for provider in model_info.allowed_providers:
            test_cases.append((model_name, provider, None))
        if ClientType.OPENROUTER in model_info.allowed_providers:
            # Add cases with each OpenRouter provider
            if model_info.openrouter_providers:
                for openrouter_provider in model_info.openrouter_providers:
                    test_cases.append((model_name, ClientType.OPENROUTER, openrouter_provider))

    # Create table
    table = Table(title="Model Manager Exhaustive Test Results")
    table.add_column("Model", justify="left", style="cyan", no_wrap=True)
    table.add_column("Requested Provider", justify="left", style="magenta")
    table.add_column("Actual Client Type", justify="left", style="green")
    table.add_column("Provider Model Name", justify="left", style="yellow")
    table.add_column("OpenRouter Provider Name", justify="left", style="red")

    # Run tests
    for model_name, provider, openrouter_provider in test_cases:
        try:
            if provider:
                if provider == ClientType.OPENROUTER:
                    client, actual_model_name = set_model(model_name, provider, openrouter_provider)
                else :
                    client, actual_model_name = set_model(model_name, provider)
            else:
                client, actual_model_name = set_model(model_name)
            table.add_row(
                model_name,
                str([model_name, provider, openrouter_provider]),
                str(client.type),
                actual_model_name,
                str(client.provider_model_store) if client.type == ClientType.OPENROUTER else "N/A"
            )
        except Exception as e:
            table.add_row(
                model_name,
                str(provider) if provider else "DEFAULT",
                "ERROR",
                str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            )

    # Print results
    console = Console()
    console.print("\nTotal test cases:", len(test_cases))
    console.print(table)
    for client in get_global_runtime().client_list:
        console.print(client.type)

if __name__ == "__main__":
    test_client_manager()
