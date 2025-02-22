import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from server.status import router as status_router
from server.connect import router as connect_router
from server.node_operator import router as operator_router


v1router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

v1router.include_router(status_router)
v1router.include_router(connect_router)
v1router.include_router(operator_router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    print("Shutting down")
    os._exit(0)


app = FastAPI(
    lifespan=lifespan,
)
app.include_router(v1router)
