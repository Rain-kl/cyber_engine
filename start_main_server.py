import os.path

from config import config
from loguru import logger

logger.add("logs/runtime.log", rotation="1 day", retention="7 days", level="DEBUG")

if __name__ == "__main__":
    import uvicorn

    if not os.path.exists("data"):
        os.makedirs("data")

    logger.info(f"loading... server will running on ws://{config.host}:{config.port}")
    uvicorn.run("websocket:app", host=config.host, port=config.port, log_level="info")
