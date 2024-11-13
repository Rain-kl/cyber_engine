import json

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):

    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)


class InputModel(BaseModel):
    role: str = "user"
    chanel: str = "qq"
    user_id: int  # 用户id
    msg: str  # 消息内容


class ResponseModel(BaseModel):
    code: int = 200
    user_id: int  # 用户id
    msg: str  # 消息内容
    data: dict = {}


class OpenaiChatMessageModel(BaseModel):
    role: str
    content: str

    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)


class TaskModel(BaseModel):
    user_id: int
    channel: str
    tasks: str
    origin: str
