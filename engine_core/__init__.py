import asyncio
import json
from typing import AsyncGenerator

from models import ChatCompletionRequest, ChatCompletionChunkResponse, TaskModel
from .agent import QopProcess
from .agent.FcAgent import instruction_to_function_mapper
# from .core import EngineCore
from .plugins import tools
from .task_db import task_center
from .utils import get_system_fingerprint, ChunkWrapper


class Ponder:
    def __init__(self, _id, _created):
        self.__chunk_wrapper = ChunkWrapper(_id=_id, _created=_created)

    async def run(self, chat_completion_request: ChatCompletionRequest) -> AsyncGenerator[
        ChatCompletionChunkResponse, None]:
        """
        核心入口，处理输入，流式输出
        :param _id:  返回对话的ID
        :param _created: 返回对话的创建时间
        :param chat_completion_request: 用户请求
        :return: 异步生成器，生成响应块
        """
        try:
            if (
                    hasattr(chat_completion_request, 'extra_body')
                    and hasattr(chat_completion_request.extra_body, 'FC_flag')
                    and chat_completion_request.extra_body.FC_flag
            ):
                # 始终生成一个初始事件，确保函数至少有一个输出
                for i in "Event: 开始任务":
                    await asyncio.sleep(0.05)
                    yield self.__chunk_wrapper.content_chunk_wrapper(i)
                yield self.__chunk_wrapper.content_chunk_wrapper("\n")
                yield self.__chunk_wrapper.content_chunk_wrapper("\n")
                #     print("FC_flag 为 True，执行 instruction_to_function_mapper")
                result = await instruction_to_function_mapper(chat_completion_request.content, tools=tools,
                                                              use_prompt=True)
                task_center.add_task(TaskModel(
                    user_id=chat_completion_request.extra_headers.authorization,
                    data=json.dumps(result)
                ))
                yield self.__chunk_wrapper.content_chunk_wrapper(str(result))
            else:
                # 添加默认行为，确保即使条件不满足也会有输出
                print("FC_flag 不存在或为 False，执行默认行为")
                qop = QopProcess(self.__chunk_wrapper)
                async for chunk in qop.run(chat_completion_request.content):
                    yield chunk
                yield self.__chunk_wrapper.content_chunk_wrapper("生成完毕")
        except Exception as e:
            # 异常处理，确保错误被捕获并返回
            print(f"ponder 函数执行错误: {e}")
            yield self.__chunk_wrapper.event_chunk_wrapper(f"处理过程中出现错误: {str(e)}")
