from loguru import logger

from model import InputModel


def parse_ws_msg(data: dict) -> InputModel:
    """
    Parse a WebSocket message.
    """
    try:
        input_model = InputModel(**data)
        return input_model
    except Exception as e:
        logger.error(f"ParseWSMessage -> Invalid data Input: {data}")
        raise e
