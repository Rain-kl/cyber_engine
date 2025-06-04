from loguru import logger

from engine_core.hmq import connect_hmq
from engine_core.utils import ChunkWrapper, XMlParser
from models import ChatCompletionRequest
from .Dispatcher import Dispatcher
from .MCPToolCall import MCPToolCall
from .Retriever import Retriever


class AgentCore:
    def __init__(
        self,
        chunk_wrapper: ChunkWrapper,
        chat_completion_request: ChatCompletionRequest,
    ):
        self.chat_completion_request = chat_completion_request
        self.chunk_wrapper = chunk_wrapper
        self.user_id = chat_completion_request.extra_headers.authorization
        self.hmq = connect_hmq(chat_completion_request.extra_headers.authorization)
        self.mcp_tool_call = MCPToolCall()

    async def run(self):
        try:
            content = self.chat_completion_request.content
            user_messages = await self.hmq.add_user_message(content)

            latest_response = ""
            support_tools = await self.mcp_tool_call.get_openai_format_tools()
            async for word in Dispatcher(support_tools).run(user_messages):
                yield self.chunk_wrapper.content_chunk_wrapper(word)
                latest_response += word
            while True:
                await self.hmq.add_user_message(latest_response)
                pce_response = XMlParser(latest_response).parse_call_expert()
                ut_response = XMlParser(latest_response).parse_function()
                if pce_response is None and ut_response is None:
                    break
                else:
                    response = pce_response if pce_response else ut_response
                    latest_response = ""
                new_response = ""
                if response.type == "call_expert":
                    if response.values[0] == "retriever":
                        async for word in Retriever().run(response.values[1]):
                            new_response += word
                            yield self.chunk_wrapper.content_chunk_wrapper(word)
                        new_response = (
                            new_response.split("<final_answer>")[1]
                            .split("</final_answer>")[0]
                            .strip()
                        )
                        new_response = f"<retriever>{new_response}</retriever>"
                elif response.type == "use_tool":
                    result = await self.mcp_tool_call.execute(
                        response.function, dict(zip(response.params, response.values))
                    )
                    if result.isError:
                        logger.error(f"工具调用失败: {result.error}")
                        new_response = f"<{response.function}>工具调用失败: {result.content}</{response.function}>"
                    else:
                        new_response = f"<{response.function}>{result.content}</{response.function}>"

                assert new_response != "", "新响应不能为空"
                user_messages = await self.hmq.add_user_message(new_response)
                async for word in Dispatcher(support_tools).run(user_messages):
                    yield self.chunk_wrapper.content_chunk_wrapper(word)
                    latest_response += word

        except Exception as e:
            logger.error(f"AgentCore处理出错: {e}")
            raise
