import json
from typing import List, Dict

from openai import AsyncOpenAI
from config import config
from model import InputModel, OpenaiChatMessageModel
from .redis_ntr import RedisSqlite


class EngineCore:
    def __init__(self, input_: InputModel):
        self.input_: InputModel = input_
        self.chat_message: List[Dict] = []
        self.message_history_key = f"{input_.user_id}_msg"

    async def _update_chat_message(self) -> List[Dict]:
        redis = RedisSqlite("./data/mq.db")
        await redis.connect()
        is_exists = await redis.exists(self.message_history_key)
        if is_exists:
            data = await redis.get(self.message_history_key)
            msg_history = json.loads(data)
        self.chat_message.append(
            OpenaiChatMessageModel(
                role="user",
                content=self.input_.msg
            ).model_dump()
        )

        return self.chat_message

    async def pond(self):
        client = AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )
        chat_message = await self._update_chat_message()
        chat_completion = await client.chat.completions.create(
            model=config.llm_model,
            temperature=0.7,
            # response_format={"type": "json_object"},
            messages=chat_message,
        )
        return chat_completion
