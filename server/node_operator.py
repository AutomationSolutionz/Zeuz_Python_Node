import os
import signal
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/operator", tags=["operator"])

class OperatorResponse(BaseModel):
    """Response model for the /kill and /restart endpoints."""

    status: Literal["ok", "error"] = "ok"
    error: str | None = None


@router.post("/kill")
def kill():
    print("[Node server] Kill signal received. Shutting down.")
    os.kill(os.getpid(), signal.SIGINT)
    return OperatorResponse(status="ok")


@router.post("/restart", status_code=501)
def restart():
    return OperatorResponse(status="error", error="Not implemented")


@router.post("/rename_node", status_code=501)
def rename_node():
    return OperatorResponse(status="error", error="Not implemented")
