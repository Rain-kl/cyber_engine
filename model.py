import json

from pydantic import BaseModel


class InputModel(BaseModel):
    user_id: int  # 用户id
    msg: str  # 消息内容

    def __str__(self):
        return json.dumps(self.model_dump())


class ResponseModel(BaseModel):
    user_id: int  # 用户id
    msg: str  # 消息内容

    def __str__(self):
        return json.dumps(self.model_dump())


class OpenaiChatMessageModel(BaseModel):
    role: str
    content: str
