import time

from ._model import BaseModel


class TaskModel(BaseModel):
    """
    事件日志模型, 用于记录用户的操作日志
    """

    user_id: str
    data: str
    status: int = 0
    created: int = int(time.time())
