from engine_core import EngineCore
from model import InputModel


def test_engine_core():
    input_ = InputModel.model_validate({
        "user_id": "user",
        "msg": "帮我发一个邮件"
    })
    engine = EngineCore(input_)
    assert engine.input_.msg == "2022 01 01 00 00 00: test message"
    assert engine.message_history_key == "test_user_msg"
    assert engine.redis.db_path == "./data/mq.db"
    assert engine.chat_message == []
