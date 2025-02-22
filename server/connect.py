from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/connect", tags=["connect"])


class ConnectRequest(BaseModel):
    """Request to connect to a server."""

    server: str
    api_key: str


@router.post("", status_code=200)
def connect(connect: ConnectRequest):
    pass
