from pydantic import BaseModel


class InputModel(BaseModel):
    username: str  # 用户名
    msg: str  # 消息内容


class ResponseModel(BaseModel):
    username: str  # 用户名
    msg: str  # 消息内容
