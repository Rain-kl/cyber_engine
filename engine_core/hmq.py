from redis_mq import RedisSqlite
from engine_core.hmdb import HMDB


class HMQueue(RedisSqlite):
    def __init__(self, user_id):
        super().__init__("./data/hmq.db")
        self.user_id = user_id
        self.max_context_length = 16  # 设置最大上下文长度为16
        self.hmdb = HMDB(user_id)  # 初始化HMDB实例

    async def get_message(self) -> list:
        """
        获取用户的消息列表，如果不存在则初始化为空列表
        """
        messages = await self.get(self.user_id)
        if not messages:
            await self.set(self.user_id, [])
            return []
        return messages

    async def add_user_message(self, value):
        """
        添加用户消息到消息列表中，如果消息已存在则不重复添加
        如果消息超过最大上下文长度，将旧消息存入数据库
        """
        messages = await self.get_message()
        if len(messages) > 0 and messages[-1]["content"] == value:
            return messages
        if len(messages) > 1 and messages[-2]["content"] == value:
            messages = messages[:-1]
            return messages
        messages.append({
            "role": "user",
            "content": value
        })

        # 如果消息超过最大上下文长度，将旧消息存入数据库
        return await self.put2db(messages)

    async def put2db(self, messages):
        if len(messages) > self.max_context_length:
            # 计算要存入数据库的消息数量
            overflow_count = len(messages) - self.max_context_length
            # 将前overflow_count条消息存入数据库
            await self.store_messages_to_db(messages[:overflow_count])
            # 保留最近的max_context_length条消息
            messages = messages[-self.max_context_length:]
        await self.set(self.user_id, messages)
        return messages

    async def add_assistant_message(self, value):
        messages = await self.get_message()
        messages.append({
            "role": "assistant",
            "content": value
        })

        # 如果消息超过最大上下文长度，将旧消息存入数据库
        return await self.put2db(messages)

    async def store_messages_to_db(self, messages):
        """将消息存储到HMDB数据库中"""
        hmdb_instance = await self.hmdb.connect()
        for message in messages:
            await hmdb_instance.add_message(
                role=message["role"],
                content=message["content"]
            )

    async def get_history_from_db(self, limit=None, offset=0):
        """从数据库中获取特定用户的历史消息"""
        hmdb_instance = await self.hmdb.connect()
        return await hmdb_instance.get_messages_by_user(
            user_id=self.user_id,
            limit=limit,
            offset=offset
        )

    async def get_all_users_history(self, limit=None, offset=0):
        """从数据库中获取所有用户的历史消息，按照时间排序"""
        hmdb_instance = await self.hmdb.connect()
        return await hmdb_instance.get_messages(limit=limit, offset=offset)


def connect_hmq(user_id) -> HMQueue:
    return HMQueue(user_id).connect()
