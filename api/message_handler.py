import time

from fastapi import WebSocket
from config import config
from engine_core import Ponder
from engine_core.utils import ChunkWrapper
from models import ChatCompletionRequest, ChatCompletionChunkResponse
from models.ChatCompletionRequest import ExtraBody
from models.openai_chat.chat_completion_chunk import Choice, ChoiceDelta
from .connection_manager import manager
from engine_core.command import commands  # 导入命令系统


def generate_id():
    """
    生成对话ID
    """
    import uuid

    return f"chatcmpl-{uuid.uuid4().hex}"


def finish_chunk(_id, created) -> ChatCompletionChunkResponse:
    return ChatCompletionChunkResponse(
        id=_id,
        model=config.virtual_model,
        choices=[
            Choice(delta=ChoiceDelta(), index=0, logprobs=None, finish_reason="stop")
        ],
        created=created,
        object="chat.completion.chunk",
        system_fingerprint=ChunkWrapper().system_fingerprint,
    )


async def handle_message(
    chat_completion_request: ChatCompletionRequest, websocket: WebSocket
) -> None:
    """
    处理WebSocket消息
    """
    init_id = generate_id()
    init_created = int(time.time())
    chunk_wrapper = ChunkWrapper(init_id, init_created)

    # 特殊指令处理
    if chat_completion_request.content.startswith("/"):
        command_path = chat_completion_request.content.split()[0]  # 获取命令路径
        if command_path in commands:
            # 执行注册的命令处理函数
            await commands[command_path](
                chat_completion_request, websocket, chunk_wrapper
            )
        else:
            # 未知命令
            for i in f"未知命令: {command_path}, 请使用 /help 获取帮助":
                await manager.send_private_stream(
                    chunk_wrapper.content_chunk_wrapper(i), websocket
                )
    else:
        # 非命令消息处理
        # chat_completion_request.extra_body = ExtraBody(FC_flag=True)
        async for chunk in Ponder(init_id, init_created, chat_completion_request).run():
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
