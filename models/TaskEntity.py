from ._model import BaseModel


class TaskModel(BaseModel):
    user_id: int
    channel: str
    tasks: str
    origin: str
