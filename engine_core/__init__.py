from openai.types.chat import ChatCompletion

from models import ChatCompletionRequest
from .core import EngineCore


async def ponder(input_: ChatCompletionRequest) -> ChatCompletion:
    engine = EngineCore(input_)
    chat_completion = await engine.pond()
    return chat_completion
