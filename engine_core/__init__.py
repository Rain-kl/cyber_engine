from models import ChatCompletionRequest, ChatCompletionChunkResponse
from .FCAgent.agent import instruction_to_function_mapper
# from .core import EngineCore
from .plugins import tools


async def ponder(chat_completion_request: ChatCompletionRequest) -> ChatCompletionChunkResponse:
    """
    核心入口，处理输入，流式输出
    :param chat_completion_request:
    :return:
    """
    # user_id = chat_completion_request.extra_headers.authorization
    # if user_id.startswith("Bearer "):
    #     user_id = user_id.replace("Bearer ", "")
    # user_profile=load_user_info(user_id)
    if chat_completion_request.extra_body.FC_flag:
        await instruction_to_function_mapper(chat_completion_request.content, tools=tools, use_prompt=True)
