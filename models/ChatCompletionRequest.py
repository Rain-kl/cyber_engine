from typing import List, Optional, Dict, Union

from ._model import BaseModel


class ContentMsg(BaseModel):
    type: str
    text: str


# 数据模型
class Message(BaseModel):
    role: str
    content: str | List[ContentMsg]


class ExtraBody(BaseModel):
    FC_flag: bool = False  # 使用function call
    RAG_flag: bool = False  # 强制使用RAG
    MIX_flag: bool = True


class ExtraHeaders(BaseModel):
    authorization: str


class ChatCompletionRequest(BaseModel):
    model: str = "ena-test"  # 模型名称
    messages: List[Message]  # 消息列表
    temperature: Optional[float] = 1.0  # 温度
    top_p: Optional[float] = 1.0  # top-p
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None
    extra_headers: ExtraHeaders | None = None  # 修复: 改为 None 而不是 (None,)
    extra_body: ExtraBody | None = None

    @property
    def content(self) -> str:
        """
        获取消息内容
        :return:
        """
        # 修复: 不修改原始消息列表，只获取最后一条消息
        if not self.messages:
            return ""

        last_message = self.messages[-1]

        if isinstance(last_message.content, str):
            return last_message.content
        elif isinstance(last_message.content, list):
            for m in last_message.content:
                if m.type == "text":
                    return m.text
        return ""

    def update_content(self, context: str) -> None:
        """
        更新上下文信息
        :param context: 新的上下文内容
        :return: None
        """
        assert self.messages is not None

        # 只更新最后一条消息
        if not self.messages:
            return

        last_message = self.messages[-1]

        if isinstance(last_message.content, str):
            last_message.content = context
        elif isinstance(last_message.content, list):
            # 修复: enumerate 返回 (index, item)，需要正确解包
            for i, m in enumerate(last_message.content):
                if m.type == "text":
                    m.text = context
                    break  # 只更新第一个找到的 text 类型内容
