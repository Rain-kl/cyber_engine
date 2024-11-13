import os.path

from loguru import logger

logger.add("logs/vdb.log", rotation="1 day", retention="7 days", level="DEBUG")

if __name__ == "__main__":
    import uvicorn

    if not os.path.exists('data'):
        os.makedirs('data')

    logger.info(f"starting vdb server on http://localhost:6899")
    logger.info(f"vdb server api docs on http://localhost:6899/docs")
    uvicorn.run("vector_db:app", port=6899, log_level="info")
