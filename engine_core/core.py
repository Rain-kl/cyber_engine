import json
from typing import AsyncGenerator

from loguru import logger

from models import ChatCompletionRequest, ChatCompletionChunkResponse, TaskModel
from .agent import QopProcess
from .agent.FcAgent.mcp_tool_call import MCPToolCall
from .agent.RouterAgent import RouterAgent
from .agent_core import AgentCore
from .hmq import connect_hmq
# from .core import EngineCore
from .task_db import task_center
from .utils import ChunkWrapper, deprecated


class Ponder:
    def __init__(self, _id, _created, chat_completion_request: ChatCompletionRequest):
        self.__chunk_wrapper = ChunkWrapper(_id=_id, _created=_created)
        self.router_agent = RouterAgent()
        self.chat_completion_request = chat_completion_request
        self.hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        self.mcp_tool_call = MCPToolCall()
        self.agent = AgentCore(self.__chunk_wrapper, chat_completion_request)

    async def run(self) -> AsyncGenerator[
        ChatCompletionChunkResponse, None]:
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
            yield self.__chunk_wrapper.event_chunk_wrapper(f"处理过程中出现错误: {str(e)}")

    @deprecated
    async def _execute_instruction(self, user_messages: list[dict[str, str]], user_id: str) -> AsyncGenerator[
        ChatCompletionChunkResponse, None]:
        """
        执行指令处理流程

        Args:
            user_messages: 用户输入内容, 包含历史记录
            user_id: 用户ID

        Returns:
            异步生成器，生成响应块
        """
        yield self.__chunk_wrapper.content_chunk_wrapper("正在处理您的指令...\n")

        #   使用FcAgent处理指令
        try:
            result = await self.mcp_tool_call.generate_tool_call(user_messages)
        except Exception as e:
            logger.trace(f"执行指令处理时出现错误: {e}")
            raise e

        if isinstance(result, list):
            # 将任务添加到任务中心
            task_center.add_task(TaskModel(
                user_id=user_id,
                data=json.dumps(result)
            ))
            yield self.__chunk_wrapper.content_chunk_wrapper("是否执行以下任务？\n")
        yield self.__chunk_wrapper.content_chunk_wrapper(str(result))
        await self.hmq.add_assistant_message(str(result))

    @deprecated
    async def _search_knowledge_base(self, content: str) -> AsyncGenerator[
        ChatCompletionChunkResponse, None]:
        """
        执行知识库查询处理流程

        Args:
            content: 用户输入问题

        Returns:
            异步生成器，生成响应块
        """
        yield self.__chunk_wrapper.content_chunk_wrapper("正在查询相关信息以回答您的问题...\n")

        # 使用QopAgent处理问题
        qop = QopProcess(self.__chunk_wrapper)
        async for chunk in qop.run(content):
            if chunk.choices[0].delta.content.startswith(">>"):
                await self.hmq.add_assistant_message(chunk.choices[0].delta.content)
            yield chunk

        yield self.__chunk_wrapper.content_chunk_wrapper("生成完毕")

    @deprecated
    async def _auto_route(self, user_messages: list[dict[str, str]], user_id: str) -> AsyncGenerator[
        ChatCompletionChunkResponse, None]:
        """
        自动路由用户输入到合适的处理方法

        Args:
            user_messages: 用户输入内容, 包含历史记录
            user_id: 用户ID

        Returns:
            异步生成器，生成响应块
        """
        # 使用路由代理判断用户输入类型
        input_type, details = await self.router_agent.run(user_messages)

        # 生成一个初始事件，指示当前处理模式
        yield self.__chunk_wrapper.content_chunk_wrapper(f"Event: 内容类型 - {input_type}\n")

        # 根据输入类型选择处理方法
        if input_type == "question":
            # 执行知识库查询处理流程
            async for chunk in self._search_knowledge_base(user_messages[-1]['content']):
                yield chunk
        else:
            # 执行指令处理流程
            async for chunk in self._execute_instruction(user_messages, user_id):
                yield chunk
