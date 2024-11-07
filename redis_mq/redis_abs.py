from abc import ABC, abstractmethod


class RedisABC(ABC):
    def __init__(
            self,
            db_path: str,
            db=0,
            password=None,
    ):
        self.db_path = db_path
        self.db = db
        self.password = password

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def length(self):
        pass

    @abstractmethod
    async def get(self, key: str) -> str:
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        pass

    @abstractmethod
    async def set(self, key: str, value: str):
        pass

    @abstractmethod
    async def lpush(self, key: str, value: str):
        pass

    @abstractmethod
    async def rpush(self, key: str, value: str):
        pass

    @abstractmethod
    async def get_list(self, key) -> list:
        pass

    @abstractmethod
    async def rpop(self, key: str) -> str:
        pass

    @abstractmethod
    async def lpop(self, key: str) -> str:
        pass

    @abstractmethod
    async def empty(self, key: str):
        pass
