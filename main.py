from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
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
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_json = json.loads(data)
            action = data_json.get("action")

            if action == "greet":
                response = {"action": "greet", "message": "Hello from server!"}
            elif action == "echo":
                response = {"action": "echo", "message": data_json.get("message", "No message provided")}
            elif action == "broadcast":
                message = data_json.get("message", "No message provided")
                await manager.broadcast(f"Client #{client_id} says: {message}")
                response = {"action": "broadcast", "message": "Broadcast message sent"}
            else:
                response = {"error": "Unknown action"}

            await manager.send_private_msg(json.dumps(response), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8000, log_level="info")
