import asyncio
import inspect
import json
from datetime import datetime
from typing import List, Dict

from loguru import logger
from openai import AsyncOpenAI
from openai.resources import AsyncChat as OpenAIAsyncChat

from config import config
from model import InputModel, OpenaiChatMessageModel
from redis_mq import RedisSqlite
from .plugins import tools, load_plugins
from .prompt import PromptGeneratorCN
from .vdb_api import Mnemonic, KDB

max_chat_message_length = config.max_chat_message_length


class UpdateStrategy:
    ALL_UPDATE = 0
    REDIS_UPDATE_ONLY = 1
    INPUT_UPDATE_ONLY = 2


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
        self.input_.msg = f"""
            当前时间{formatted_time}\n
            message:{self.input_.msg}
        """

    @staticmethod
    async def build_message_LTM(input_model: InputModel) -> OpenaiChatMessageModel:
        logger.debug("start build_message_LTM")

        mn = Mnemonic()
        related_history = await mn.search(input_model.msg, user_id=input_model.user_id)
        assert related_history.status == 200, "Failed to get related history"
        related_data = []
        for i in related_history.data:
            if float(i.distance) < 0.8:
                related_data.append(i.text)
        print(f"""
                这是与上一条消息相关的参考信息，如果与实际消息无任何关系，请忽略\n
                相关历史:{related_data}\n
                """)
        return OpenaiChatMessageModel(
            role="system",
            content=f"""
                这是与上一条消息相关的参考信息，如果与实际消息无任何关系，请忽略\n
                相关历史:{related_data}\n
                """
        )

    async def _update_chat_message(self, update_strategy=UpdateStrategy.ALL_UPDATE) -> List[Dict]:
        await self.redis.connect()
        is_exists = await self.redis.exists(self.message_history_key)
        if is_exists:
            data = await self.redis.get(self.message_history_key)
            msg_history = json.loads(data)
            self.chat_message.extend(msg_history)

        if update_strategy == UpdateStrategy.ALL_UPDATE:
            if self.input_:
                self.chat_message.append(
                    OpenaiChatMessageModel(
                        role="user",
                        content=self.input_.msg
                    ).model_dump()
                )
        return self.chat_message

    async def pond(self, update_strategy=UpdateStrategy.ALL_UPDATE) -> OpenAIAsyncChat.completions:
        client = AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )
        chat_message = await self._update_chat_message(update_strategy)

        logger.debug("start chat")

        async def create_chat_completion():
            logger.debug("start create_chat_completion")
            ltm_msg = await self.build_message_LTM(self.input_)
            return await client.chat.completions.create(
                model=config.llm_model,
                temperature=0.7,
                # response_format={"type": "json_object"},
                messages=[PromptGeneratorCN().generate_init.model_dump()]
                         + chat_message
                         + [ltm_msg],
                tools=tools,
            )

        chat_completion = await create_chat_completion()

        return await self.chat_completion_process(chat_completion)

    async def chat_completion_process(
            self, chat_completion: OpenAIAsyncChat.completions
    ) -> OpenAIAsyncChat.completions:
        """
        处理chat_completion的结果, 并执行工具函数。最后更新进入redis的消息历史，并清空input_
        :param chat_completion:
        :return:
        """
        if chat_completion.choices[0].message.tool_calls:
            for tool_call in chat_completion.choices[0].message.tool_calls:

                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_args['input_'] = self.input_

                logger.debug(f"tool_name - {tool_name}")
                logger.debug(f"tool_args - {tool_args}")
                try:
                    tool = load_plugins()[tool_name]
                    if inspect.iscoroutinefunction(tool):
                        tool_result = await asyncio.create_task(tool(**tool_args))
                    else:
                        tool_result = tool(**tool_args)

                    if tool_result:
                        content = f"已执行函数{tool_name}, 参数: {tool_args}, 结果: {tool_result}"
                    else:
                        content = f"函数{tool_name}没有返回结果",
                    logger.debug(f"tool_result: {tool_result}")
                    self.chat_message.append(
                        OpenaiChatMessageModel(
                            role="system",
                            content=content,
                        ).model_dump()
                    )
                except Exception as e:
                    logger.error(f"执行函数{tool_name}运行时错误，错误捕获：{e}")
                    self.chat_message.append(
                        OpenaiChatMessageModel(
                            role="system",
                            content=f"执行函数{tool_name}运行时错误，错误捕获：{e},请将错误原因发送给用户"
                        ).model_dump()
                    )
                if len(self.chat_message) >= max_chat_message_length:
                    logger.debug("chat_message length >= max_chat_message_length")
                    await Mnemonic().add(json.dumps(self.chat_message[0]), user_id=self.input_.user_id)
                    self.chat_message.pop(0)
            await self.redis.set(self.message_history_key, json.dumps(self.chat_message, ensure_ascii=False))
            self.chat_message = []
            self.input_ = None
            return await self.pond()
        else:
            self.chat_message.append(
                OpenaiChatMessageModel(
                    role=chat_completion.choices[0].message.role,
                    content=chat_completion.choices[0].message.content,
                ).model_dump()
            )
            if len(self.chat_message) >= max_chat_message_length:
                logger.debug("chat_message length >= max_chat_message_length")
                await Mnemonic().add(json.dumps(self.chat_message[0]), user_id=self.input_.user_id)
                self.chat_message.pop(0)

            await self.redis.set(self.message_history_key, json.dumps(self.chat_message, ensure_ascii=False))
            self.chat_message = []
            self.input_ = None
            return chat_completion
