from venv import logger

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

from model import ResponseModel
from .ws_utils import ParseWSMessage
import json

app = FastAPI()


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
        logger.debug(f"Sending message: {message}")
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_channel}")
async def websocket_endpoint(websocket: WebSocket, client_channel: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
            except:
                await manager.send_private_msg("Invalid JSON", websocket)
                continue
            try:
                print(data)
                input_ = ParseWSMessage(data)
            except:
                await manager.send_private_msg("Invalid Input", websocket)
                continue
            await manager.send_private_msg(
                json.dumps(
                    ResponseModel(
                        user_id=int(input_.user_id),
                        msg=str(input_.msg)
                    ).model_dump()
                ),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client #{client_channel} left the chat")
        # await manager.broadcast(f"Client #{client_channel} left the chat")
