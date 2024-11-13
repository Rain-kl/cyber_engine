from typing import List

from fastapi import WebSocket
from loguru import logger

from model import ResponseModel


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_private_msg(message: ResponseModel, websocket: WebSocket):
        if isinstance(message, ResponseModel):
            logger.info(f"Send -> {message}")
            await websocket.send_text(message.__str__())
        else:
            raise Exception(f"Error: {message} is not a ResponseModel object")

    async def __broadcast(self, message: ResponseModel):
        for connection in self.active_connections:
            logger.info(f"Broadcast -> {message}")
            await connection.send_text(message.__str__())


manager = ConnectionManager()
