import asyncio
import time

from fastapi import WebSocket
from config import config
from engine_core import ponder
from engine_core.utils import get_system_fingerprint
from models import ChatCompletionRequest, ChatCompletionChunkResponse
from models.openai_chat.chat_completion_chunk import Choice, ChoiceDelta
from .connection_manager import manager


def generate_id():
    """
    chatcmpl-B7I93tP1RlCwjy7CsGKJh07Kt07bg
    :return:
    """
    import uuid
    return f"chatcmpl-{uuid.uuid4().hex}"


def finish_chunk(_id, created) -> ChatCompletionChunkResponse:
    return ChatCompletionChunkResponse(
        id=_id,
        model=config.virtual_model,
        choices=[
            Choice(
                delta=ChoiceDelta(),
                index=0,
                logprobs=None,
                finish_reason="stop"
            )],
        created=created,
        object="chat.completion.chunk",
        system_fingerprint=get_system_fingerprint()
    )


async def handle_message(chat_completion_request: ChatCompletionRequest, websocket: WebSocket) -> None:
    """
    Handle incoming message from websocket
    :param chat_completion_request:
    :param websocket:
    :return:
    """
    init_id = generate_id()
    init_created = int(time.time())
    # TODO: Implement the following
    for chunk in await ponder(init_id, init_created, chat_completion_request):
        await manager.send_private_stream(chunk, websocket)
    await manager.send_private_stream(finish_chunk(init_id, init_created), websocket)

    # for i in "Hello World":
    #     await asyncio.sleep(0.3)
    #     chunk = ChatCompletionChunkResponse(
    #         id=init_id,
    #         model=config.virtual_model,
    #         choices=[
    #             Choice(
    #                 delta=ChoiceDelta(
    #                     role="assistant",
    #                     content=i,
    #                 ),
    #                 index=0,
    #                 logprobs=None,
    #                 finish_reason=None
    #             )],
    #         created=init_created,
    #         object="chat.completion.chunk",
    #         system_fingerprint=get_system_fingerprint()
    #     )
    #     await manager.send_private_stream(chunk, websocket)
