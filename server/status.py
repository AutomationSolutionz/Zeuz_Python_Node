from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/status", tags=["status"])


class StateExecutionDetail(BaseModel):
    """Returns the current state of the execution in Node."""

    runid: str
    tc_id: str
    step_sequence: int
    action_sequence: int
    variables: dict[str, str]
    logs: list[str]


class ConnectionStateResponse(BaseModel):
    """Returns the current state of the Node."""

    connected_server: str
    execution_detail: StateExecutionDetail | None = None


class StatusResponse(BaseModel):
    """Returns the current state of the Node."""

    state: Literal["idle", "in_progress"]


@router.get("")
def status():
    return StatusResponse(state="idle")
