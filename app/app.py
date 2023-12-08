import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .servicies import Settings, Database
from .api.router import create_api_router


def create_app(settings: Settings) -> FastAPI:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        filename="app.log",
        filemode="w",
    )

    # db = Database(settings)
    app = FastAPI(
        title="Misis Banach Space go Algo",
        version="0.0.1",
        description="Rest api for frontend Application",
        docs_url=f"{settings.api_prefix}/docs",
        openapi_url=f"{settings.api_prefix}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_credentials=True,
        allow_headers=["*"],
    )
    api_router = create_api_router(prefix=settings.api_prefix)

    app.include_router(api_router)
    return app
