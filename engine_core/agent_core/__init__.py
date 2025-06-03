from loguru import logger

from engine_core.utils import ChunkWrapper, XMlParser
from engine_core.hmq import connect_hmq
from models import ChatCompletionRequest
from .Dispatcher import Dispatcher
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

    async def run(self):
        try:
            content = self.chat_completion_request.content
            user_messages = await self.hmq.add_user_message(content)

            latest_response = ""
            async for word in Dispatcher().run(user_messages):
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
                        new_response = new_response.split("<final_answer>")[1].split("</final_answer>")[0].strip()
                        new_response = f"<retriever>{new_response}</retriever>"
                elif response.type == "use_tool":
                    for word in f"\n 使用工具: {response.function}，参数: {response.params}, 值: {response.values}":
                        yield self.chunk_wrapper.content_chunk_wrapper(word)
                    new_response = f"<{response.function}>执行完毕</{response.function}>"

                assert new_response != "", "新响应不能为空"
                user_messages = await self.hmq.add_user_message(new_response)
                async for word in Dispatcher().run(user_messages):
                    yield self.chunk_wrapper.content_chunk_wrapper(word)
                    latest_response += word


        except Exception as e:
            logger.error(f"AgentCore处理出错: {e}")
            raise
