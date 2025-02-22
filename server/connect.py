import time
from fastapi import APIRouter
from pydantic import BaseModel

from Framework.Utilities import ConfigModule
from Framework.deploy_handler import long_poll_handler
from Framework.node_server_state import STATE

router = APIRouter(prefix="/connect", tags=["connect"])


class ConnectRequest(BaseModel):
    """Request to connect to a server."""

    server: str
    api_key: str


def set_new_credentials(server, api_key):
    """Store new credentials in the settings file."""
    AUTHENTICATION_TAG = "Authentication"
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "api-key")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "api-key", api_key)
    ConfigModule.remove_config_value(AUTHENTICATION_TAG, "server_address")
    ConfigModule.add_config_value(AUTHENTICATION_TAG, "server_address", server)


@router.post("", status_code=200)
def connect(new_conn_info: ConnectRequest):
    # Request for the server to connect to another server by stopping the
    # connection loop with the deploy service.
    long_poll_handler.STOP_NEXT_ITERATION = True
    # TODO: Instead of overwriting the config value directly, we should use some
    # kind of queue to pass on the information to node cli to reset the api key
    # on next iteration.

    # Wait for at least 10m for the node to stop processing the next test case.
    for i in range(60 * 10):
        if STATE.state == "idle":
            break
        time.sleep(1)

    set_new_credentials(new_conn_info.server, new_conn_info.api_key)
