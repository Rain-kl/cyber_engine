import struct
from loguru import logger

from model import InputModel


def ParseWSMessage(data: dict) -> InputModel:
    """
    Parse a WebSocket message.
    """
    input_model = InputModel(**data)
    return input_model
