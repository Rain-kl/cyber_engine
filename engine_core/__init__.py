from model import InputModel
from config import config
from .core import EngineCore


async def ponder(input_: InputModel) -> str:
    engine = EngineCore(input_)
    chat_completion = await engine.pond()
    return chat_completion.choices[0].message.content
