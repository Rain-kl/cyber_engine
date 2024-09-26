import asyncio
import json
import time
from os import times

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from loguru import logger
from engine_core import ponder
from model import ResponseModel
from .ws_utils import ParseWSMessage

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
        logger.debug(f"Send -> {message}")
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


async def handle_message(data: str, websocket: WebSocket):
    """
    Handle incoming message from websocket
    :param data:
    :param websocket:
    :return:
    """
    try:
        data = json.loads(data)
        input_ = ParseWSMessage(data)
    except (ValueError, TypeError) as e:
        await manager.send_private_msg(f"Invalid Input: {str(e)}", websocket)
        return

    # Message Processed
    pond_msg = await ponder(input_)

    response_data = ResponseModel(
        user_id=int(input_.user_id),
        msg=str(pond_msg)
    ).model_dump()

    await manager.send_private_msg(json.dumps(response_data, ensure_ascii=False), websocket)


@app.websocket("/ws/{client_channel}")
async def websocket_endpoint(websocket: WebSocket, client_channel: str):
    await manager.connect(websocket)

    tasks = []
    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(f"Received <- {data}")
            task = asyncio.create_task(handle_message(data, websocket))
            tasks.append(task)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client #{client_channel} left the chat")
    finally:
        if tasks:
            await asyncio.gather(*tasks)
