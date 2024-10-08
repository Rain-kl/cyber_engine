from typing import List

from fastapi import WebSocket
from loguru import logger


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_private_msg(message: str, websocket: WebSocket):
        logger.info(f"Send -> {message}")
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            logger.info(f"Broadcast -> {message}")
            # await connection.send_text(message)


manager = ConnectionManager()
