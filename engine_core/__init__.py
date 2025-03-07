from models import ChatCompletionRequest, ChatCompletionChunkResponse
from models.openai_chat.chat_completion_chunk import Choice, ChoiceDelta

from config import config

# from .core import EngineCore
from .plugins import tools
from .utils import get_system_fingerprint
from .agent.FCAgent import instruction_to_function_mapper


async def ponder(_id, _created, chat_completion_request: ChatCompletionRequest) -> ChatCompletionChunkResponse:
    """
    核心入口，处理输入，流式输出
    :param _id:  返回对话的ID
    :param _created: 返回对话的创建时间
    :param chat_completion_request: 用户请求
    :return:
    """
    ##TODO: authorization
    # user_id = chat_completion_request.extra_headers.authorization
    # if user_id.startswith("Bearer "):
    #     user_id = user_id.replace("Bearer ", "")
    # user_profile=load_user_info(user_id)
    chunk_generator = ChunkWrapper(_id, _created)
    yield chunk_generator.event_chunk_wrapper("开始任务")

    if chat_completion_request.extra_body.FC_flag:
        await instruction_to_function_mapper(chat_completion_request.content, tools=tools, use_prompt=True)


class ChunkWrapper:
    def __init__(self, _id, _created):
        self._id = _id
        self._created = _created

    def event_chunk_wrapper(self, event_content):
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
