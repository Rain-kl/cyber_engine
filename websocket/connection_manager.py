import time
import uuid
from typing import List

from fastapi import WebSocket
from loguru import logger
from models import ChatCompletionResponse, ChatCompletionChunkResponse
from models.openai_chat.chat_completion_chunk import ChatCompletionChunk
from models.openai_chat.chat_completion_message import ChatCompletionMessage
from models.openai_chat.chat_completion import Choice


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    @staticmethod
    async def send_private_msg(message: str, websocket: WebSocket):
        if not isinstance(message, str):
            raise ValueError("Message must be a string")
        chunk_id = f"chatcmpl-{uuid.uuid4().hex}"
        response = ChatCompletionResponse(
            id=chunk_id,
            model="ena-test",
            created=int(time.time()),
            object="chat.completion",
            choices=[Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=message,
                    role="assistant",
                )
            )]
        )
        logger.info(f"Send -> {message}")
        await websocket.send_text(response.__str__())

    @staticmethod
    async def send_private_stream(chunk: ChatCompletionChunkResponse, websocket: WebSocket):
        if not isinstance(chunk, ChatCompletionChunkResponse):
            raise ValueError("Chunk must be a ChatCompletionChunkResponse")
        await websocket.send_text(f"data: {chunk.__str__()}\n\n")

    @staticmethod
    async def send_private_exception(exception: Exception, websocket: WebSocket):
        await websocket.send_text(exception.__str__())

    async def __broadcast(self, message: ChatCompletionChunk):
        for connection in self.active_connections:
            logger.info(f"Broadcast -> {message}")
            await connection.send_text(message.__str__())


manager = ConnectionManager()
