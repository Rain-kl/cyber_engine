import os
import importlib
import json
from datetime import datetime
from typing import List, Dict

import openai.resources
from loguru import logger
from openai import AsyncOpenAI

from config import config
from model import InputModel, OpenaiChatMessageModel
from .redis_ntr import RedisSqlite
from .prompt import PromptGeneratorCN
from .plugins import tools

plugins_folder = os.path.join(os.path.dirname(__file__), "plugins")


def load_plugins():
    plugins = {}
    for filename in os.listdir(plugins_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"engine_core.plugins.{module_name}")
            # 将每个模块中的函数添加到插件字典中
            for attr in dir(module):
                if callable(getattr(module, attr)) and not attr.startswith("_"):
                    plugins[attr] = getattr(module, attr)
    return plugins


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

    async def chat_completion_process(self, chat_completion: openai.resources.AsyncChat.completions):
        if chat_completion.choices[0].message.tool_calls:
            for tool_call in chat_completion.choices[0].message.tool_calls:
                try:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    logger.debug(f"tool_name - {tool_name}")
                    logger.debug(f"tool_args - {tool_args}")
                    tool = load_plugins()[tool_name]
                    tool_result = tool(**tool_args)
                    if tool_result:
                        content = f"已执行函数{tool_name}, 参数: {tool_args}, 结果: {tool_result}"
                    else:
                        content = f"函数{tool_name}没有返回结果",

                    self.chat_message.append(
                        OpenaiChatMessageModel(
                            role="system",
                            content=content,
                        ).model_dump()
                    )
                    if len(self.chat_message) >= 10:
                        self.chat_message.pop(0)

                except Exception as e:
                    logger.error(f"Error: {e}")
            await self.redis.set(self.message_history_key, json.dumps(self.chat_message))
            return await self.pond()
        else:
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

    async def pond(self) -> openai.resources.AsyncChat.completions:
        client = AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )
        chat_message = await self._update_chat_message()

        logger.debug("start chat")
        chat_completion = await client.chat.completions.create(
            model=config.llm_model,
            temperature=0.7,
            # response_format={"type": "json_object"},
            messages=[PromptGeneratorCN().generate_init.model_dump()] + chat_message,
            tools=tools,
        )
        return await self.chat_completion_process(chat_completion)
