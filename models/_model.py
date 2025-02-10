import json

from pydantic import BaseModel as _BaseModel


class BaseModel(_BaseModel):

    def __str__(self):
        return json.dumps(self.model_dump(), ensure_ascii=False)
