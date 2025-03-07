import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from loguru import logger

from models.ChatCompletionRequest import ExtraHeaders
from .connection_manager import manager
from .handle_message import handle_message
# from .scheduler import scheduled_broadcast
from .ws_utils import parse_input_msg
from .client_list import websocket_list

app = FastAPI()


@app.websocket("/{authorization}")
async def websocket_endpoint(websocket: WebSocket, authorization: str):
    # TODO: authorization
    await manager.connect(websocket)
    logger.info(f"User #{authorization} joined the chat")
    websocket_list[authorization] = websocket
    tasks = []
    try:
        # schedule_task = asyncio.create_task(scheduled_broadcast())
        # tasks.append(schedule_task)

        while True:
            received_text = await websocket.receive_text()
            try:
                data = json.loads(received_text)
                completion_request = parse_input_msg(data)
            except (ValueError, TypeError) as e:
                await manager.send_private_exception(TypeError("Invalid formate"), websocket)
                return

            logger.info(f"Received <- {data}")
            if completion_request.content.startswith("/"):
                await manager.send_private_msg("Command not supported yet", websocket_list[authorization])
            else:
                completion_request.extra_headers = ExtraHeaders(authorization=authorization)
                task = asyncio.create_task(handle_message(completion_request, websocket))
                tasks.append(task)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client #{authorization} left the chat")
    finally:
        if tasks:
            await asyncio.gather(*tasks)
