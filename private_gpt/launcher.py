"""FastAPI app creation, logger configuration and main API routes."""
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from injector import Injector

# from private_gpt.server.chat.chat_router import chat_router
# from private_gpt.server.chunks.chunks_router import chunks_router
# from private_gpt.server.embeddings.embeddings_router import embeddings_router
# from private_gpt.server.health.health_router import health_router
# from private_gpt.server.ingest.ingest_router import ingest_router

from private_gpt.routers.chat_router import chat_router
from private_gpt.routers.chunks_router import chunks_router
from private_gpt.routers.ingest_router import ingest_router
from private_gpt.routers.user import user_router
from private_gpt.settings.settings import Settings

logger = logging.getLogger(__name__)


def create_app(root_injector: Injector) -> FastAPI:

    # Start the API
    async def bind_injector_to_request(request: Request) -> None:
        request.state.injector = root_injector

    app = FastAPI(dependencies=[Depends(bind_injector_to_request)])

    app.include_router(chat_router)
    app.include_router(chunks_router)
    app.include_router(ingest_router)
    app.include_router(user_router)
    # app.include_router(embeddings_router)
    # app.include_router(health_router)

    settings = root_injector.get(Settings)
    if settings.server.cors.enabled:
        logger.debug("Setting up CORS middleware")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if settings.ui.enabled:
        logger.debug("Importing the UI module")
        from private_gpt.ui.ui import PrivateGptUi

        ui = root_injector.get(PrivateGptUi)
        ui.mount_in_app(app, settings.ui.path)

    return app
