"""FastAPI application entrypoint: uvicorn main:app --app-dir src"""
import logging
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.settings import settings
from core.manager_db_async import init_db, async_engine
from applications.login.router import login_router
from applications.pacientes.router import paciente_router


def create_app() -> FastAPI:
    logger = logging.getLogger("nutricion")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("server is starting")
        if settings.ENVIRONMENT == "local":
            await init_db()  # no schema DDL in staging/production
        try:
            yield
        finally:
            await async_engine.dispose()
            logger.info("server is shutting down")

    app = FastAPI(
        title="Nutricion service", version="0.1.0",
        description="A simple web service for a nutricion",
        openapi_url="/openapi.json", docs_url="/docs",
        root_path="/nutricion", lifespan=lifespan,
    )
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    app.add_middleware(
        CORSMiddleware, allow_origins=origins,
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
    )
    app.state.logger = logger
    app.include_router(login_router)
    app.include_router(paciente_router)
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host=settings.FASTAPI_RUN_HOST, port=settings.FASTAPI_RUN_PORT)
