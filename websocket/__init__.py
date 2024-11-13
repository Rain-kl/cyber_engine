import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger

from model import ResponseModel
from .connection_manager import manager
from .handle_message import handle_message
from .scheduler import scheduled_broadcast
from .ws_utils import parse_ws_msg
from .ws_clients import websocket_list

app = FastAPI()


@app.websocket("/{client_channel}")
async def websocket_endpoint(websocket: WebSocket, client_channel: str):
    await manager.connect(websocket)
    logger.info(f"Client #{client_channel} joined the chat")
    websocket_list[client_channel] = websocket

    tasks = []
    try:
        schedule_task = asyncio.create_task(scheduled_broadcast())
        tasks.append(schedule_task)

        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(data)
                input_ = parse_ws_msg(data)
            except (ValueError, TypeError) as e:
                await manager.send_private_msg(f"Invalid Input: {str(e)}", websocket)
                return

            logger.info(f"Received <- {data}")
            if input_.msg.startswith("/"):
                await manager.send_private_msg(ResponseModel(
                    user_id=input_.user_id,
                    msg="Command not supported yet"
                ), websocket_list[client_channel])
            else:
                task = asyncio.create_task(handle_message(input_, websocket))
                tasks.append(task)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client #{client_channel} left the chat")
    finally:
        if tasks:
            await asyncio.gather(*tasks)
