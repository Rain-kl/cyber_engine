from .ChunkWrapper import ChunkWrapper
from .Parser import Parser, XMlParser, JsonParser
from openai import AsyncOpenAI


def get_openai_client():
    return AsyncOpenAI()


__all__ = ["ChunkWrapper", "Parser", "XMlParser", "JsonParser","get_openai_client"]
