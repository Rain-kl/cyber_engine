import asyncio
import json
import time
from http.client import HTTPException

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from loguru import logger

from models import ChatCompletionRequest
from models.ChatCompletionRequest import ExtraHeaders
from .client_list import websocket_list
from .connection_manager import manager
from .message_handler import handle_message
from .websocket_client import client
# from .scheduler import scheduled_broadcast
from .ws_utils import parse_input_msg

app = FastAPI()
MODEL_NAME = "ena-test"
WAIT_TIMEOUT = 20


@app.websocket("/v1/{authorization}")
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
                completion_request.extra_headers = ExtraHeaders(
                    authorization=authorization
                )
            except (ValueError, TypeError) as e:
                await manager.send_private_exception(
                    TypeError("Invalid formate"), websocket
                )
                return e

            logger.info(f"Received <- {data}")
            task = asyncio.create_task(handle_message(completion_request, websocket))
            tasks.append(task)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        logger.info(f"Client #{authorization} left the chat")
    finally:
        if tasks:
            await asyncio.gather(*tasks)



@app.post("/v1/chat/completions")
async def stream_data(request: Request, completion_request: ChatCompletionRequest):
    authorization = request.headers.get("authorization").replace("Bearer ", "")
    completion_request.extra_headers = ExtraHeaders(authorization=authorization)
    logger.info("start")
    await client.connect(f"ws://localhost:6898/v1/{authorization}")
    await client.send_message(completion_request)

    async def get_response_stream():
        try:
            while True:
                try:
                    # Add wait_for_timeout-second timeout for receive_message
                    response = await asyncio.wait_for(client.receive_message(), timeout=WAIT_TIMEOUT)
                    if not response.startswith("data:"):
                        raise ValueError("Invalid response format")
                    else:
                        yield response
                        if response.strip() == "data: [DONE]":
                            break
                except asyncio.TimeoutError:
                    # Format error using OpenAI error format
                    error_response = {
                        "error": {
                            "message": f"Request timed out after waiting for {WAIT_TIMEOUT} seconds",
                            "type": "timeout_error",
                            "code": "timeout_error"
                        }
                    }
                    yield f"data: {json.dumps(error_response)}\n\n"
                    yield "data: [DONE]\n\n"
                    break
        except Exception as e:
            logger.error(f"Error in stream: {str(e)}")
            error_response = {
                "error": {
                    "message": f"An error occurred: {str(e)}",
                    "type": "server_error",
                    "code": "server_error"
                }
            }
            yield f"data: {json.dumps(error_response)}\n\n"
            yield "data: [DONE]\n\n"
            client.close()

    return StreamingResponse(get_response_stream(), media_type="text/event-stream")


@app.get("/v1/models")
async def list_models():
    """
    返回可用模型列表
    """
    current_time = int(time.time())
    models = [
        {"id": MODEL_NAME, "object": "model", "created": current_time - 100000,
         "owned_by": "ryan"},
    ]

    response = {
        "object": "list",
        "data": models
    }
    return JSONResponse(content=response)
