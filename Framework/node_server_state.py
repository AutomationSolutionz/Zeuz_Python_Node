from typing import Literal


class ServerState:
    state: Literal["idle", "in_progress"] = "idle"

STATE: ServerState = ServerState()
