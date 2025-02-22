# Author: sazid

from typing import Any, Callable
import traceback
import time
import random
import requests
from colorama import Fore

from Framework.Utilities import RequestFormatter
from Framework.node_server_state import STATE


class DeployHandler:
    """
    DeployHandler is responsible for maintaining the connection with deploy
    service and fetch any necessary resources to run test cases.
    """

    COMMAND_DONE = b"DONE"
    COMMAND_CANCEL = b"CANCEL"
    ERROR_PREFIX = b"error"


    def __init__(
        self,
        on_connect_callback: Callable[[bool], None],
        response_callback: Callable[[Any], None],
        cancel_callback: Callable[[], None],
        done_callback: Callable[[], bool],
    ) -> None:
        self.on_connect_callback = on_connect_callback
        self.response_callback = response_callback
        self.cancel_callback = cancel_callback

        # Done callback should return true if node does not want to run anymore
        # test cases, false otherwise.
        self.done_callback = done_callback

        self.backoff_time = 0


    def on_message(self, message) -> bool:
        """Returns True if the handler should quit, False otherwise."""

        if message == self.COMMAND_DONE:
            # We're done for this run session.
            return self.done_callback()

        elif message == self.COMMAND_CANCEL:
            # Run cancelled by the user/service.
            self.cancel_callback()
            return False

        self.response_callback(message)
        return False


    def on_error(self, error) -> None:
        print("[deploy] Error communicating with the deploy service.")
        print(error)
        if self.backoff_time < 6:
            self.backoff_time += 1


    def run(self, host: str) -> None:
        reconnect = False
        server_online = False
        while True:
            if STATE.reconnect_with_credentials is not None:
                break

            if reconnect:
                if server_online:
                    time.sleep(0.1)
                else:
                    time.sleep(random.randint(1, 3))

            self.on_connect_callback(reconnect)

            try:
                reconnect = True
                resp = RequestFormatter.request("get", host, verify=False)

                if resp.content.startswith(self.ERROR_PREFIX):
                    server_online = False
                    self.on_error(resp.content)
                    continue

                if resp.status_code == requests.codes['no_content']:
                    server_online = False
                    continue

                if not resp.ok:
                    server_online = False
                    print("[deploy] facing difficulty communicating with the server, status code:", resp.status_code, " | reconnecting")
                    try:
                        print(Fore.YELLOW + str(resp.content))
                    except Exception:
                        pass

                    # Encountered a server error, retry.
                    time.sleep(random.randint(1, 3))
                    return

                should_quit = self.on_message(resp.content)
                if should_quit:
                    break

                reconnect = False
                server_online = True
            except requests.exceptions.ReadTimeout:
                pass
            except Exception:
                traceback.print_exc()
                print("[deploy] RETRYING...")
