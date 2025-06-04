from typing import AsyncGenerator

from loguru import logger

from models import ChatCompletionRequest, ChatCompletionChunkResponse
from .agent_core import AgentCore
from .hmq import connect_hmq
# from .core import EngineCore
from .utils import ChunkWrapper


class Ponder:
    def __init__(self, _id, _created, chat_completion_request: ChatCompletionRequest):
        self.__chunk_wrapper = ChunkWrapper(_id=_id, _created=_created)
        self.chat_completion_request = chat_completion_request
        self.hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        self.agent = AgentCore(self.__chunk_wrapper, chat_completion_request)

    async def run(self) -> AsyncGenerator[ChatCompletionChunkResponse, None]:
        """
        核心入口，处理输入，流式输出

        Returns:
            异步生成器，生成响应块
        """
        try:
            async for chunk in self.agent.run():
                yield chunk
            yield self.__chunk_wrapper.finish_chunk()

        except Exception as e:
            # 异常处理，确保错误被捕获并返回
            logger.exception(f"处理过程中出现错误: {str(e)}")
            yield self.__chunk_wrapper.event_chunk_wrapper(
                f"处理过程中出现错误: {str(e)}"
            )