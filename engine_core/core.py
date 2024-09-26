import json
from datetime import datetime
from typing import List, Dict

from openai import AsyncOpenAI

from config import config
from model import InputModel, OpenaiChatMessageModel
from .redis_ntr import RedisSqlite
from .prompt import PromptGeneratorCN


class EngineCore:
    def __init__(self, input_: InputModel):
        self.input_: InputModel = input_
        self.chat_message: List[Dict] = []
        self.message_history_key = f"{input_.user_id}_msg"
        self.redis = RedisSqlite("./data/mq.db")

        self.input_processing()

    def input_processing(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y %m %d %H %M %S")
        self.input_.msg = f"{formatted_time}: {self.input_.msg}"

    async def _update_chat_message(self) -> List[Dict]:
        await self.redis.connect()
        is_exists = await self.redis.exists(self.message_history_key)
        if is_exists:
            data = await self.redis.get(self.message_history_key)
            msg_history = json.loads(data)
            self.chat_message.extend(msg_history)
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
            messages=[PromptGeneratorCN().generate_init.model_dump()] + chat_message,
        )
        self.chat_message.append(
            OpenaiChatMessageModel(
                role=chat_completion.choices[0].message.role,
                content=chat_completion.choices[0].message.content,
            ).model_dump()
        )
        if len(self.chat_message) >= 10:
            self.chat_message.pop(0)
        await self.redis.set(self.message_history_key, json.dumps(self.chat_message))
        return chat_completion
