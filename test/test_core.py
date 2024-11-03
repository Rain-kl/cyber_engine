import json

import pytest
from openai import AsyncOpenAI

from config import config
from engine_core import EngineCore
from engine_core.utils import Intention_recognition
from model import InputModel


def test_engine_core():
    input_ = InputModel.model_validate({
        "user_id": "user",
        "msg": "帮我发一个邮件"
    })
    engine = EngineCore(input_)
    assert engine.input_.msg == "2022 01 01 00 00 00: test message"
    assert engine.MHK == "test_user_msg"
    assert engine.redis.db_path == "./data/mq.db"
    assert engine.chat_message == []


class TestRedisSqlite:
    """测试RedisSqlite类的异步方法"""

    @pytest.mark.asyncio
    async def test_Intention_recognition(self):
        client = AsyncOpenAI(
            base_url=config.llm_base_url,
            api_key=config.llm_api_key,
        )
        model = config.llm_model
        msg = "帮我发一个邮件"
        result = await Intention_recognition(client, model, msg)
        type_data = json.loads(result.choices[0].message.content)
        assert type_data["type"] == "command"
        msg = "你好，今天过得好吗"
        result = await Intention_recognition(client, model, msg)
        type_data = json.loads(result.choices[0].message.content)
        assert type_data["type"] == "useless"
