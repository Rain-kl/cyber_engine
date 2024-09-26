
from config import config
from loguru import logger

logger.add("logs/runtime.log", rotation="1 day", retention="7 days", level="DEBUG")

if __name__ == "__main__":
    import uvicorn

    logger.info(f"websocket server running on ws://{config.host}:{config.port}")
    uvicorn.run("websocket:app", host=config.host, port=config.port, log_level="info")
