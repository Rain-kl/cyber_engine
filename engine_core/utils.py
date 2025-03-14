from collections.abc import Callable
from typing import Dict, Any, Generator
import json

import json
from typing import Dict

from openai import AsyncOpenAI

from config import config
from models import ChatCompletionChunkResponse
from models.openai_chat.chat_completion_chunk import Choice, ChoiceDelta, ChatCompletionChunk


# from .core import EngineCore


def get_system_fingerprint():
    """
    fp_b705f0c291
    :return:
    """
    return "fp_b705f0c291"


# async def ltm_build_msg(input_model: InputModel) -> OpenaiChatMessageModel:
#     logger.debug("start ltm_build_message")
#
#     mn = Mnemonic()
#     related_history = await mn.search(input_model.msg, user_id=input_model.user_id)
#     assert related_history.status == 200, "Failed to get related history"
#     related_data = []
#     for i in related_history.data:
#         if float(i.distance) < 0.8:
#             related_data.append(i.text)
#     print(f"""
#             相关历史:{related_data}\n
#             """)
#     return OpenaiChatMessageModel(
#         role="system",
#         content=f"""
#             这是与上一条消息相关的参考信息，如果与实际消息无任何关系，请忽略\n
#             相关历史:{related_data}\n
#             """
#     )

def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=config.llm_base_url,
        api_key=config.llm_api_key,
    )


async def intention_recognition(client: AsyncOpenAI, model, msg: str) -> Dict:
    """
    useless, question, command, other
    :param model: model name
    :param client: AsyncOpenAI
    :param msg: user message
    :return: {"type": "useless"}
    """
    prompt = """
        You are a problem classifier, and you need to determine which category the user's input belongs to
        Current classification: \n
            useless: meaningless information, such as greetings related to greeting\n
            other : other types of information，such as questions, commands, etc.\n
        Return the judgment result in JSON format as follows:\n
            {
            type: 'useless'
            }
    """
    type_data = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": msg
            }
        ],
        temperature=0.3,
        max_tokens=100,
        response_format={"type": "json_object"}
    )
    return json.loads(type_data.choices[0].message.content)


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
                    finish_reason=None
                )],
            created=self._created,
            object="chat.completion.chunk",
            system_fingerprint=get_system_fingerprint()
        )

    def step_chunk_wrapper_stream(self, step_tag, step_func: Callable, *args, **kwargs) -> Generator[
        ChatCompletionChunk, None, None]:
        yield self.content_chunk_wrapper(f"<step>[{step_tag}]")
        response: str = step_func(*args, **kwargs)
        for i in response:
            yield self.content_chunk_wrapper(i)
        yield self.content_chunk_wrapper("</step>")
        yield self.content_chunk_wrapper("\n\n\n")

    def content_chunk_wrapper(self, content, line_break=False) -> ChatCompletionChunkResponse:
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
