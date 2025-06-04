from loguru import logger
from models import ChatCompletionRequest


def parse_input_msg(data: dict) -> ChatCompletionRequest:
    """
    Parse a WebSocket message.
    """
    try:
        input_model = ChatCompletionRequest(**data)
        return input_model
    except Exception as e:
        logger.error(f"ParseWSMessage -> Invalid data Input: {data}")
        raise e
