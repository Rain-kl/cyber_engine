import json

from fastapi import WebSocket

from engine_core import ponder
from model import ResponseModel
from .connection_manager import manager
from .ws_utils import ParseWSMessage


async def handle_message(data: str, websocket: WebSocket) -> None:
    """
    Handle incoming message from websocket
    :param data:
    :param websocket:
    :return:
    """
    try:
        data = json.loads(data)
        input_ = ParseWSMessage(data)
    except (ValueError, TypeError) as e:
        await manager.send_private_msg(f"Invalid Input: {str(e)}", websocket)
        return

    pond_msg = await ponder(input_)
    response_data = ResponseModel(
        user_id=int(input_.user_id),
        msg=str(pond_msg)
    )

    await manager.send_private_msg(response_data, websocket)
