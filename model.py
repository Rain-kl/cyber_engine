from pydantic import BaseModel


class InputModel(BaseModel):
    user_id: int  # 用户名
    msg: str  # 消息内容


class ResponseModel(BaseModel):
    user_id: int  # 用户名
    msg: str  # 消息内容
