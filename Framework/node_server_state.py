from pydantic import BaseModel
from typing import Literal


class LoginCredentials(BaseModel):
    server: str
    api_key: str


class ServerState(BaseModel):
    state: Literal["idle", "in_progress"] = "idle"

    # Control variable to stop the next iteration of the deplopy service
    # connection loop.
    reconnect_with_credentials: LoginCredentials | None = None

STATE: ServerState = ServerState()
