from ..clients.openai_client import ClientOpenAI
from ..core.engine import ToolEngine
import dotenv, os

dotenv.load_dotenv()

def setup_test(model="gpt-4o-mini"):
    client = ClientOpenAI.create_openai(os.getenv("OPENAI_API_KEY"))
    engine = ToolEngine(client, model)
    return client, engine