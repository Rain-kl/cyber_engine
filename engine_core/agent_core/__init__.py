from loguru import logger

from engine_core.utils import ChunkWrapper, XMlParser
from models import ChatCompletionRequest
from .Dispatcher import Dispatcher
from .Retriever import Retriever


class AgentCore:
    def __init__(
            self,
            chunk_wrapper: ChunkWrapper,
            chat_completion_request: ChatCompletionRequest,
    ):
        self.chunk_wrapper = chunk_wrapper
        self.user_id = chat_completion_request.extra_headers.authorization

        pass

    async def run(self, user_message: str):
        try:
            latest_response = ""
            async for word in Dispatcher().run(user_message):
                yield self.chunk_wrapper.content_chunk_wrapper(word)
                latest_response += word

            while (response := XMlParser(latest_response).parse_call_expert()) is not None:
                print(response)
                latest_response = ""
                if response.function == "call_expert":
                    if response.values[0] == "retriever":
                        async for word in Retriever().run(response.values[1]):
                            yield self.chunk_wrapper.content_chunk_wrapper(word)

        except Exception as e:
            logger.error(f"AgentCore处理出错: {e}")
            raise
