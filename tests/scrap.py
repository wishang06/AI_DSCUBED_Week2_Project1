from framework.clients.model_manager import ModelManager
from framework.types.models import ModelInstanceRequest
from framework.core.engine import SinglePassEngine
from pprint import pprint


model = ModelManager().get_model_instance(
    ModelInstanceRequest(model_name="o3-mini", model_extras={"reasoning_effort": "low"})
)
pprint(model)
engine = SinglePassEngine(model=model)
response = engine.execute("Hello!")
pprint(response.full.model_dump())
