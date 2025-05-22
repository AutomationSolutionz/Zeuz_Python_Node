import logging
from typing import Any
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.status import router as status_router
from server.connect import router as connect_router
from server.evaluator import router as evaluator_router
from server.node_operator import router as operator_router
from server.mobile import router as mobile_router
from server.mac import router as mac_router

class EndpointFilter(logging.Filter):
    def __init__(
        self,
        path: str,
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find(self._path) == -1

def main() -> FastAPI:
    # Filter out /endpoint
    logging.getLogger("uvicorn.access").addFilter(EndpointFilter(path="/status"))

    v1router = APIRouter(
        prefix="/api/v1",
        tags=["v1"],
    )

    v1router.include_router(status_router)
    v1router.include_router(connect_router)
    v1router.include_router(operator_router)
    v1router.include_router(evaluator_router)
    v1router.include_router(mobile_router)
    v1router.include_router(mac_router)
    app = FastAPI()
    app.include_router(v1router)

    origins = [
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


if __name__ == "__main__":
    main()
