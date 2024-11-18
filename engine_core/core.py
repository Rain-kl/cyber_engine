import asyncio
import inspect
import json
from datetime import datetime
from typing import Dict

from loguru import logger
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from config import config
from model import InputModel, OpenaiChatMessageModel
from redis_mq import RedisSqlite
from rag_core.sdk_vdb import Mnemonic
from .plugins import tools, load_plugin
from .prompt import PromptGeneratorCN
from .utils import ltm_build_msg, intention_recognition

max_chat_message_length = config.max_chat_message_length


class ChatMessageList(list):
    def __init__(self):
        super().__init__()

    def dump_json(self):
        import json
        return json.dumps(self, ensure_ascii=False)


class EngineCore:

    def __init__(self, input_: InputModel):
        self.input_: InputModel = input_
        self.input_backup = input_
        self.chat_message: ChatMessageList[Dict] = ChatMessageList()
        self.MHK = f"{input_.user_id}_msg"
        self.redis = RedisSqlite("./data/mq.db")

        self.client = AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )

        self.__input_processing()

    def __input_processing(self):
        """
        对input_进行处理，将时间格式化
        :return:
        """
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y %m %d %H %M %S")
        self.input_.msg = f"""
            time: {formatted_time}\n
            msg: {self.input_.msg}
        """

    async def __append_chat_message(self, __obj: OpenaiChatMessageModel):
        """
        添加消息到chat_message中，如果长度超过max_chat_message_length，将最早的消息pop出来
        :param __obj:
        :return:
        """
        pop_obj: Dict | None = None
        if len(self.chat_message) >= max_chat_message_length:
            pop_obj = self.chat_message.pop(0)
        self.chat_message.append(__obj.model_dump())
        await self.redis.set(self.MHK, self.chat_message.dump_json())
        if pop_obj:
            await self.__pop_item_process(OpenaiChatMessageModel(**pop_obj))

    async def __pop_item_process(self, item: OpenaiChatMessageModel):
        """
        弹出的消息处理, 如果item不为空，将其存入记忆库
        :param item:
        :return:
        """
        if item:
            logger.debug(f"pop item: {item}")
            if item.role == "user" or "assistant":
                await Mnemonic().add(item.__str__(), user_id=self.input_backup.user_id)

    async def __update_chat_message(self) -> ChatMessageList[Dict]:
        """
        更新chat_message, 从redis中获取历史消息
        不会讲本轮消息加入到历史消息中，需要手动使用__append_chat_message来添加
        :return:
        """
        self.chat_message = ChatMessageList()
        await self.redis.connect()
        is_exists = await self.redis.exists(self.MHK)
        if is_exists:
            data = await self.redis.get(self.MHK)
            msg_history = json.loads(data)
            self.chat_message.extend(msg_history)
        return self.chat_message

    async def pond(self) -> ChatCompletion:
        chat_message = await self.__update_chat_message()
        if self.input_:
            intention = await intention_recognition(client=self.client, model=config.llm_simple_model,
                                                    msg=self.input_.msg)
        else:
            intention = {"type": "useless"}
        if intention['type'] == 'useless':
            logger.debug("useless")
            ocm = OpenaiChatMessageModel(
                role="user",
                content=self.input_.msg
            )
            chat_completion = await self.client.chat.completions.create(
                model=config.llm_model,
                temperature=config.llm_temperature,
                # response_format={"type": "json_object"},
                messages=[PromptGeneratorCN().generate_init.model_dump()] + [ocm.model_dump()],
            )
        else:
            ocm = OpenaiChatMessageModel(
                role="user",
                content=self.input_.msg
            )
            await self.__append_chat_message(ocm)

            logger.debug("chat")

            ltm_msg = await ltm_build_msg(self.input_)
            chat_completion = await self.client.chat.completions.create(
                model=config.llm_model,
                temperature=config.llm_temperature,
                # response_format={"type": "json_object"},
                messages=[PromptGeneratorCN().generate_init.model_dump()]
                         + chat_message
                         + [ltm_msg],
                tools=tools,
            )

        return await self.chat_completion_process(chat_completion)

    async def chat_completion_process(self, chat_completion: ChatCompletion) -> ChatCompletion:
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
                    tool = load_plugin(tool_name)
                    if inspect.iscoroutinefunction(tool):  # 判断是否是异步函数
                        tool_result = await asyncio.create_task(tool(**tool_args))
                    else:
                        tool_result = tool(**tool_args)

                    if tool_result:
                        content = f"已执行函数{tool_name}, 参数: {tool_args}, 结果: {tool_result}"
                    else:
                        content = f"函数{tool_name}没有返回结果",
                    logger.debug(f"tool_result: {tool_result}")
                    await self.__append_chat_message(
                        OpenaiChatMessageModel(
                            role="system",
                            content=content,
                        )
                    )
                except Exception as e:
                    logger.error(f"执行函数{tool_name}运行时错误，错误捕获：{e}")
                    await self.__append_chat_message(
                        OpenaiChatMessageModel(
                            role="system",
                            content=f"执行函数{tool_name}运行时错误，错误捕获：{e},请将错误原因发送给用户"
                        )
                    )

            self.input_ = None
            return await self.pond()
        else:
            await self.__append_chat_message(
                OpenaiChatMessageModel(
                    role=chat_completion.choices[0].message.role,
                    content=chat_completion.choices[0].message.content,
                )
            )

            self.input_ = None
            return chat_completion

    async def organize_memory(self, memory_model: InputModel):

        pass
