import os
import re
import subprocess
from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import CommonUtil
from Framework.node_server_state import STATE


def _get_version() -> str | None:
    # When launched by node_runner, CWD is ZeuZ_Node-<version>
    dirname = os.path.basename(os.getcwd())
    m = re.match(r"ZeuZ_Node-(.+)", dirname)
    if m:
        return m.group(1)
    # Fallback: git branch
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=3,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None

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
    version: str | None = None


@router.get("")
def status():
    try:
        node_id = CommonUtil.MachineInfo().getLocalUser().lower()
        username, id = node_id.split("_", 1)
        if len(username) == 0:
            node_id = id
    except Exception:
        node_id = "unknown"
    return StatusResponse(state=STATE.state, node_id=node_id, version=_get_version())
