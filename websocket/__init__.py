import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger

from .connection_manager import manager
from .handle_message import handle_message
from .scheduler import scheduled_broadcast
from .ws_utils import ParseWSMessage

app = FastAPI()


@app.websocket("/ws/{client_channel}")
async def websocket_endpoint(websocket: WebSocket, client_channel: str):
    await manager.connect(websocket)

    tasks = []
    try:
        schedule_task = asyncio.create_task(scheduled_broadcast())
        tasks.append(schedule_task)

        while True:
            data = await websocket.receive_text()
            logger.info(f"Received <- {data}")
            task = asyncio.create_task(handle_message(data, websocket))
            tasks.append(task)


    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client #{client_channel} left the chat")
    finally:
        if tasks:
            await asyncio.gather(*tasks)
