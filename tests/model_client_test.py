from framework.clients.model_manager import ModelManager
from framework.utils.runtime import init_global_runtime
from framework.types.clients import ClientType
from framework.types.models import ModelInstanceRequest
from rich.console import Console
from rich.table import Table
import dotenv

dotenv.load_dotenv()


def test_model_manager():
    # Initialize runtime and model manager
    init_global_runtime()
    manager = ModelManager()

    # Create table
    table = Table(title="Model Manager Test Results")
    table.add_column("Model Name", justify="left", style="cyan", no_wrap=True)
    table.add_column("Requested Provider", justify="left", style="magenta")
    table.add_column("OpenRouter Provider", justify="left", style="red")
    table.add_column("Provider Type", justify="left", style="green")
    table.add_column("Provider Model Name", justify="left", style="yellow")
    table.add_column("Model Extras", justify="left", style="blue")

    # Get all models from registry
    test_cases = []
    for model_name in manager.registry.list_models():
        model_info = manager.registry.get_model(model_name)

        # Add case with default provider
        test_cases.append((model_name, None, None))

        # Add cases with each allowed provider
        for provider in model_info.allowed_providers:
            test_cases.append((model_name, provider, None))

            # Add OpenRouter provider cases if applicable
            if provider == ClientType.OPENROUTER and model_info.openrouter_providers:
                for or_provider in model_info.openrouter_providers:
                    test_cases.append((model_name, provider, or_provider))

    # Run tests
    console = Console()
    for model_name, provider, or_provider in test_cases:
        try:
            # Create model instance request
            request = ModelInstanceRequest(
                model_name=model_name,
                provider=provider,
                openrouter_provider=or_provider,
                model_extras={"temperature": 0.7} if provider else None,
            )

            # Get model instance
            instance = manager.get_model_instance(request)

            table.add_row(
                model_name,
                str(provider) if provider else "DEFAULT",
                str(instance.openrouter_provider),
                str(instance.provider.type),
                instance.provider_model_name,
                str(instance.model_extras) if instance.model_extras else "N/A",
            )

        except Exception as e:
            table.add_row(
                model_name,
                str(provider) if provider else "DEFAULT",
                str(or_provider) if or_provider else "N/A",
                "ERROR",
                str(e)[:50] + "..." if len(str(e)) > 50 else str(e),
                "N/A",
            )

    # Print results
    console.print("\nTotal test cases:", len(test_cases))
    console.print(table)


if __name__ == "__main__":
    test_model_manager()
