from fastapi import WebSocket

# from engine_core import ponder
from models import ChatCompletionRequest, ChatCompletionChunkResponse
from .connection_manager import manager


async def handle_message(_input: ChatCompletionRequest, websocket: WebSocket) -> None:
    """
    Handle incoming message from websocket
    :param _input:
    :param websocket:
    :return:
    """
    # TODO: Implement the following
    # pond_msg = await ponder(_input)
    # response_data = ChatCompletionChunkResponse(
    #     user_id=int(_input.user_id),
    #     msg=str(pond_msg.choices[0].message.content),
    #     data=pond_msg.model_dump()
    # )
    response_data = "Hello World"
    await manager.send_private_msg(response_data, websocket)
