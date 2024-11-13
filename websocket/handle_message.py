from fastapi import WebSocket

from engine_core import ponder
from model import ResponseModel, InputModel
from .connection_manager import manager


async def handle_message(input_: InputModel, websocket: WebSocket) -> None:
    """
    Handle incoming message from websocket
    :param input_:
    :param websocket:
    :return:
    """
    pond_msg = await ponder(input_)
    response_data = ResponseModel(
        user_id=int(input_.user_id),
        msg=str(pond_msg.choices[0].message.content),
        data=pond_msg.model_dump()
    )

    await manager.send_private_msg(response_data, websocket)
