from pydantic import BaseModel
from typing import List


class SearchResponseModel(BaseModel):
    text: str
    distance: str


class APIBaseResponseModel(BaseModel):
    status: int
    message: str


class APISearchResponseModel(APIBaseResponseModel):
    data: List[SearchResponseModel]
