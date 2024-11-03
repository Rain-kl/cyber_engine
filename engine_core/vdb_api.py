import httpx
from pydantic import BaseModel
from typing import List


class MemoryModel(BaseModel):
    memory: str
    user_id: int


class SearchResultModel(BaseModel):
    text: str
    distance: str


class SearchResponseModel(BaseModel):
    status: int
    message: str
    data: List[SearchResultModel]


class NetApi:
    def __init__(self):
        self.host = "http://localhost:6899"

    def endpoint(self, path: str):
        assert path.startswith("/"), "Path must start with /"
        return f"{self.host}{path}"


class Mnemonic(NetApi):
    def __init__(self):
        super().__init__()

    async def add(self, memory: str, user_id: int):
        params = {
            "memory": memory,
            "user_id": user_id
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.endpoint("/mn/add"), params=params)
            return response

    async def search(self, query: str, user_id: int) -> SearchResponseModel:
        params = {
            "query": query,
            "user_id": user_id
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.endpoint("/mn/search"), params=params)
            return SearchResponseModel(**response.json())


class KDB(NetApi):
    def __init__(self):
        super().__init__()
