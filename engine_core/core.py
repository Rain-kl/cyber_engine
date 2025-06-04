import textwrap
import time
from typing import AsyncGenerator

from loguru import logger

from models import ChatCompletionRequest, ChatCompletionChunkResponse
from .agent_core import AgentCore
# from .core import EngineCore
from .utils import ChunkWrapper


class Ponder:
    def __init__(self, _id, _created, chat_completion_request: ChatCompletionRequest):
        self.__chunk_wrapper = ChunkWrapper(_id=_id, _created=_created)
        self.chat_completion_request = chat_completion_request

    @staticmethod
    def context_enhancement(context: str) -> str:
        """
        上下文增强方法，可以在这里实现对输入上下文的增强处理
        例如，添加更多的上下文信息或进行格式化等操作

        Args:
            context (str): 输入的上下文字符串

        Returns:
            str: 增强后的上下文字符串
        """
        # 这里可以添加具体的上下文增强逻辑
        current_time = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        enhanced_context = textwrap.dedent(f"""
        <user>{context}</user> 
        <context_package> 
            <environment_info>
                <timestamp>{current_time}</timestamp>
                <location>武汉</location>
            </environment_info>
            <retrieved_ltm>
                 <layer1>用户小王,身份学生, 住在湖北中医药大学学生公寓</layer1>
                 <layer2></layer2>
                 <layer3>用户如果需要检查天气情况,如果天气恶劣给用户设置通知提醒</layer3>
            </retrieved_ltm> 
         </context_package>
        """).strip()
        return enhanced_context

    async def run(self) -> AsyncGenerator[ChatCompletionChunkResponse, None]:
        """
        核心入口，处理输入，流式输出

        Returns:
            异步生成器，生成响应块
        """
        try:
            self.chat_completion_request.update_content(self.context_enhancement(self.chat_completion_request.content))
            # print(self.chat_completion_request)
            agent_coordination = AgentCore(self.__chunk_wrapper, self.chat_completion_request)

            async for chunk in agent_coordination.run():
                yield chunk
            yield self.__chunk_wrapper.finish_chunk()

        except Exception as e:
            # 异常处理，确保错误被捕获并返回
            logger.exception(f"处理过程中出现错误: {str(e)}")
            yield self.__chunk_wrapper.event_chunk_wrapper(
                f"处理过程中出现错误: {str(e)}"
            )
