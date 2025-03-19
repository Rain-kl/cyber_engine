import pytest

from engine_core import ponder
from models.ChatCompletionRequest import ChatCompletionRequest, Message, ExtraBody


# def test_engine_core():
#     input_ = InputModel.model_validate({
#         "user_id": "user",
#         "msg": "帮我发一个邮件"
#     })
#     engine = EngineCore(input_)
#     assert engine.input_.msg == "2022 01 01 00 00 00: test message"
#     assert engine.MHK == "test_user_msg"
#     assert engine.redis.db_path == "./data/mq.db"
#     assert engine.chat_message == []


class TestRedisSqlite:
    """测试RedisSqlite类的异步方法"""

    @pytest.mark.asyncio
    async def test_fc_agent(self):
        completion = ChatCompletionRequest(
            extra_body=ExtraBody(
                FC_flag=True
            ),
            messages=[Message(
                role="user",
                content="给123456的qq邮箱发一个问好邮件，内容你来写"
            )]
        )
        await ponder(completion)
        pass
