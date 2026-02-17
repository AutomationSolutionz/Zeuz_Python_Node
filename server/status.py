from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import CommonUtil
from Framework.node_server_state import STATE

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
    node_id: str | None = None


@router.get("")
def status():
    try:
        node_id = CommonUtil.MachineInfo().getLocalUser().lower()
        username, id = node_id.split("_", 1)
        if len(username) == 0:
            node_id = id
    except Exception:
        node_id = "unknown"
    return StatusResponse(state=STATE.state, node_id=node_id)
