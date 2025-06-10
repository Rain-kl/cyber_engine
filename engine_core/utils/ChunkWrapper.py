from collections.abc import Callable
from http.client import HTTPException
from typing import Generator

from config import config
from models import ChatCompletionChunkResponse
from models.ServerException import ServerException
from models.openai_chat.chat_completion_chunk import (
    Choice,
    ChoiceDelta,
    ChatCompletionChunk,
)


class ChunkWrapper:
    system_fingerprint = "fp_b705f0c291"

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
                    finish_reason=None,
                )
            ],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=self.system_fingerprint,
        )

    def step_chunk_wrapper(self, step_tag, step_content) -> ChatCompletionChunkResponse:
        return ChatCompletionChunkResponse(
            id=self._id,
            model=config.virtual_model,
            choices=[
                Choice(
                    delta=ChoiceDelta(
                        role="assistant",
                        content=f"<step>[{step_tag}]{step_content}</step>\n\n\n",
                    ),
                    index=0,
                    logprobs=None,
                    finish_reason=None,
                )
            ],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=self.system_fingerprint,
        )

    def step_chunk_wrapper_stream(
            self, step_tag, step_func: Callable, *args, **kwargs
    ) -> Generator[ChatCompletionChunk, None, None]:
        yield self.content_chunk_wrapper(f"<step>[{step_tag}]")
        response: str = step_func(*args, **kwargs)
        for i in response:
            yield self.content_chunk_wrapper(i)
        yield self.content_chunk_wrapper("</step>")
        yield self.content_chunk_wrapper("\n\n\n")

    def content_chunk_wrapper(
            self, content: str, line_break=False
    ) -> ChatCompletionChunkResponse:
        if line_break:
            content = content + "\n\n"
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
                    finish_reason=None,
                )
            ],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=self.system_fingerprint,
        )

    def finish_chunk(self) -> ChatCompletionChunkResponse:
        return ChatCompletionChunkResponse(
            id=self._id,
            model=config.virtual_model,
            choices=[
                Choice(
                    delta=ChoiceDelta(), index=0, logprobs=None, finish_reason="stop"
                )
            ],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=self.system_fingerprint,
        )

    @staticmethod
    def exception_chunk(e: Exception):
        return ServerException(500, f"Internal Server Error: {str(e)}")
