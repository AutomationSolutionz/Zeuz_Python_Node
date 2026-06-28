from fastapi import APIRouter
from pydantic import BaseModel

from Framework.node_server_state import STATE, LoginCredentials

router = APIRouter(prefix="/connect", tags=["connect"])


class ConnectRequest(BaseModel):
    """Request to connect to a server."""

    server: str
    api_key: str


async def set_new_credentials(server: str, api_key: str):
    """Store new credentials in the settings file."""
    server = server.strip()
    api_key = api_key.strip()
    STATE.reconnect_with_credentials = LoginCredentials(
        server=server,
        api_key=api_key,
    )
    STATE.connected_server = None
    STATE.target_server = server or None
    STATE.last_connect_error = None
    STATE.connection_state = "authenticating" if server and api_key else "disconnected"


@router.post("", status_code=200)
async def connect(new_conn_info: ConnectRequest):
    # Request for the server to connect to another server by stopping the
    # connection loop with the deploy service.

    print(f"[Node server] Connect request received from {new_conn_info.server}. Connecting...")
    await set_new_credentials(new_conn_info.server, new_conn_info.api_key)
    print(f"[Node server] Connection request processed. Node will reconnect to {new_conn_info.server}")
    return {"status": "success", "message": "Reconnection initiated"}
