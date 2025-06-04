from fastapi import FastAPI

from .api import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="UserAudit API", description="API for user audit", version="1.0.0"
    )

    # Include the API router
    app.include_router(router, prefix="/ua")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
