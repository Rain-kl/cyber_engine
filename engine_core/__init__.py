import asyncio
import json
from typing import Any, AsyncGenerator

from models import ChatCompletionRequest, ChatCompletionChunkResponse, TaskModel
from models.openai_chat.chat_completion_chunk import Choice, ChoiceDelta, ChatCompletionChunk

from config import config

# from .core import EngineCore
from .plugins import tools
from .task_db import task_center
from .utils import get_system_fingerprint
from .agent.FCAgent import instruction_to_function_mapper


async def ponder(_id, _created, chat_completion_request: ChatCompletionRequest) -> AsyncGenerator[
    ChatCompletionChunkResponse, None]:
    """
    核心入口，处理输入，流式输出
    :param _id:  返回对话的ID
    :param _created: 返回对话的创建时间
    :param chat_completion_request: 用户请求
    :return: 异步生成器，生成响应块
    """
    chunk_generator = ChunkWrapper(_id, _created)

    # 始终生成一个初始事件，确保函数至少有一个输出
    for i in "Event: 开始任务":
        await asyncio.sleep(0.05)
        yield chunk_generator.content_chunk_wrapper(i)
    yield chunk_generator.content_chunk_wrapper("\n")
    yield chunk_generator.content_chunk_wrapper("\n")

    try:
        if (
                hasattr(chat_completion_request, 'extra_body')
                and hasattr(chat_completion_request.extra_body, 'FC_flag')
                and chat_completion_request.extra_body.FC_flag
        ):
            #     print("FC_flag 为 True，执行 instruction_to_function_mapper")
            result = await instruction_to_function_mapper(chat_completion_request.content, tools=tools, use_prompt=True)
            task_center.add_task(TaskModel(
                user_id=chat_completion_request.extra_headers.authorization,
                data=json.dumps(result)
            ))
            yield chunk_generator.content_chunk_wrapper(str(result))
        else:
            # 添加默认行为，确保即使条件不满足也会有输出
            print("FC_flag 不存在或为 False，执行默认行为")
            yield chunk_generator.content_chunk_wrapper("执行默认处理流程")
    except Exception as e:
        # 异常处理，确保错误被捕获并返回
        print(f"ponder 函数执行错误: {e}")
        yield chunk_generator.event_chunk_wrapper(f"处理过程中出现错误: {str(e)}")


class ChunkWrapper:
    def __init__(self, _id, _created):
        self._id = _id
        self._created = _created

    def event_chunk_wrapper(self, event_content) -> ChatCompletionChunkResponse:
        return ChatCompletionChunkResponse(
            id=self._id,
            model=config.virtual_model,
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        role="assistant",
                        content="Event: " + event_content + "\n",
                    ),
                    index=0,
                    logprobs=None,
                    finish_reason=None
                )],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=get_system_fingerprint()
        )

    def content_chunk_wrapper(self, content):
        return ChatCompletionChunkResponse(
            id=self._id,
            model=config.virtual_model,
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        role="assistant",
                        content=content,
                    ),
                    index=0,
                    logprobs=None,
                    finish_reason=None
                )],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=get_system_fingerprint()
        )

    def finish_chunk(self) -> ChatCompletionChunkResponse:
        return ChatCompletionChunkResponse(
            id=self._id,
            model=config.virtual_model,
            choices=[
                Choice(
                    delta=ChoiceDelta(),
                    index=0,
                    logprobs=None,
                    finish_reason="stop"
                )],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=get_system_fingerprint()
        )
