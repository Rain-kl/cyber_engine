import json
from typing import List

import websockets
from loguru import logger

from models import ChatCompletionRequest


class WebSocketClient:
    def __init__(self):
        self.uri = None
        self.websocket = None
        self.temp_mq: List[ChatCompletionRequest] = []

    async def connect(self, uri: str):
        self.uri = uri
        self.websocket = await websockets.connect(self.uri)
        logger.success("Connected!")

    async def send_message(self, message: ChatCompletionRequest):
        """
        发送消息到核心
        :param message:
        :return:
        """
        if self.websocket:
            try:
                await self.websocket.send(
                    json.dumps(message.model_dump(), ensure_ascii=False)
                )
                logger.success("Process -> engine")

            except websockets.exceptions.ConnectionClosedError:
                self.temp_mq.append(message)

    async def send_tmq(self):
        """
        发送临时消息队列中的消息
        :return:
        """
        if self.temp_mq:
            await self.send_message(self.temp_mq[0])
            self.temp_mq.pop(0)

    async def receive_message(self) -> str:
        """
        从核心接收消息
        :return:
        """
        if self.websocket:
            try:
                response = await self.websocket.recv()
                return response
            except websockets.exceptions.ConnectionClosedError:
                logger.critical("Cyber Engine Connection Lost!")
                await self.connect(self.uri)
        else:
            raise ConnectionError("WebSocket is not connected.")

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            logger.success("Connection closed!")


client = WebSocketClient()
