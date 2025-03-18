from redis_mq import RedisSqlite


class HMQueue(RedisSqlite):
    def __init__(self, user_id):
        super().__init__("./data/hmq.db")
        self.user_id = user_id

    async def get_message(self) -> list:
        messages = await self.get(self.user_id)
        if not messages:
            await self.set(self.user_id, [])
            return []
        return messages

    async def add_user_message(self, value):
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
        await self.set(self.user_id, messages)
        return messages

    async def add_assistant_message(self, value):
        messages = await self.get_message()
        messages.append({
            "role": "assistant",
            "content": value
        })
        await self.set(self.user_id, messages)
        return messages


def connect_hmq(user_id) -> HMQueue:
    return HMQueue(user_id).connect()
