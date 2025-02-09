from dotenv import load_dotenv
from framework.chat.chat import Chat
from framework.clients.model_manager import ModelManager
from framework.types.models import ModelInstanceRequest
from framework.core.engine import SinglePassEngine
from framework.utils.runtime import init_global_runtime


def main():
    # Load environment variables
    load_dotenv()

    # Initialize the runtime
    init_global_runtime()

    # Set up model and engine
    model_manager = ModelManager()
    model_instance = model_manager.get_model_instance(
        ModelInstanceRequest(
            model_name="gpt-4o-mini",  # or whatever model you want to use
        )
    )

    # Create engine
    engine = SinglePassEngine(model=model_instance, streaming=True)

    # Create and run chat interface
    chat = Chat(engine)
    chat.run()


if __name__ == "__main__":
    main()
