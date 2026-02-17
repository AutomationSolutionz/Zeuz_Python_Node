from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/eval", tags=["eval"])


class EvalResponse(BaseModel):
    status: Literal["ok", "error"] = "ok"
    content: str | None = None
    error: str | None = None


@router.post("", status_code=501)
def evaluator():
    """Evaluate code on the node directly."""
    return EvalResponse(status="error", error="Not implemented")
