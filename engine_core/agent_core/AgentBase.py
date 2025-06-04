from abc import ABC, abstractmethod
from openai import AsyncOpenAI

from config import config


class AgentBase(ABC):
    @staticmethod
    def openai_client():
        return AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )

    @abstractmethod
    def _prompt(self, **kwargs): ...

    @abstractmethod
    def run(self, *args, **kwargs): ...
