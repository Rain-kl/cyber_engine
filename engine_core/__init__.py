from openai.types.chat import ChatCompletion

from model import InputModel
from .core import EngineCore


async def ponder(input_: InputModel) -> ChatCompletion:
    engine = EngineCore(input_)
    chat_completion = await engine.pond()
    return chat_completion
