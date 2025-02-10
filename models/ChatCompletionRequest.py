from typing import List, Optional, Dict, Union

from ._model import BaseModel


class ContentMsg(BaseModel):
    type: str
    text: str


# 数据模型
class Message(BaseModel):
    role: str
    content: str | List[ContentMsg]


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    extra_headers: dict | None = None,