from .core import EmbeddingVectorDB

# api/__init__.py

from fastapi import FastAPI
from .api_mnemonic import router as mnemonic_router
from .api_kdb import router as kb_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Vector DB",
        description="API for vector database",
        version="1.0.0"
    )

    # Include the API router
    app.include_router(mnemonic_router, prefix="/mn")
    app.include_router(kb_router, prefix="/kb")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
