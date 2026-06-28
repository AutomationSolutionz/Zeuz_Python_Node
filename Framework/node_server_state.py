from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel


class LoginCredentials(BaseModel):
    server: str
    api_key: str


class ServerState(BaseModel):
    state: Literal["idle", "in_progress"] = "idle"
    started_at: str = datetime.now(timezone.utc).isoformat()
    instance_id: str = str(uuid4())
    connection_state: Literal[
        "disconnected",
        "authenticating",
        "connected",
        "offline",
        "failed",
    ] = "disconnected"
    connected_server: str | None = None
    target_server: str | None = None
    last_connect_error: str | None = None

    # Control variable to stop the next iteration of the deplopy service
    # connection loop.
    reconnect_with_credentials: LoginCredentials | None = None

STATE: ServerState = ServerState()
