from loguru import logger
import sys
import time
from tests.testing_utils import read_openai_response

response = read_openai_response("tests/test_responses_objects/openai_response.json")


logger.remove()
logger.add("logs/test.log", level="DEBUG")
for n in range(20):
    logger.debug(response)
    time.sleep(1)