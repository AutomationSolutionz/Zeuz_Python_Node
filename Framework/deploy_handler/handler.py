# Author: sazid

# import websocket
import time
from urllib import response
from websocket import WebSocketApp
from typing import Callable
import threading
import sys
import signal
from pathlib import Path
sys.path.append(str(Path.cwd() / "Framework" / "pb" / "v1"))

# from Framework.pb.v1 import deploy_response_message_pb2
from pb.v1.deploy_response_message_pb2 import DeployResponse
import proto_adapter


class DeployHandler:
    """
    DeployHandler is responsible for maintaining the connection with deploy
    service and fetch any necessary resources to run test cases.
    """

    COMMAND_DONE = "DONE"
    COMMAND_CANCEL = "CANCEL"
    COMMAND_NEXT = "NEXT"


    def __init__(
        self,
        response_callback: Callable[[DeployResponse], None],
        cancel_callback: Callable[[None], None],
        done_callback: Callable[[None], None],
    ) -> None:
        self.ws = None
        self.response_callback = response_callback
        self.cancel_callback = cancel_callback
        self.done_callback = done_callback


    def on_message(self, ws: WebSocketApp, message) -> None:
        if message == self.COMMAND_DONE:
            # We're done for this run session.
            print("[deploy] Run complete.")
            self.done_callback()
            return

        elif message == self.COMMAND_CANCEL:
            # Run cancelled by the user/service.
            print("[deploy] Run cancelled.")
            self.cancel_callback()
            return

        response = DeployResponse()
        response.ParseFromString(message)

        self.response_callback(response)

        ws.send(self.COMMAND_NEXT)


    def on_error(self, ws: WebSocketApp, error) -> None:
        print("[deploy] Error communicating with the deploy service.")
        print(error)


    def on_close(self, ws: WebSocketApp, close_status_code: int, close_msg) -> None:
        print("[deploy] Connection closed.")


    def on_open(self, ws: WebSocketApp) -> None:
        print("[deploy] Connected to deploy service.")
        ws.send(self.COMMAND_NEXT)


    def signal_handler(self, sig, frame):
        self.cancel_callback()
        print("[deploy] Received interrupt signal (Ctrl-C), disconnecting from service...")

        if self.ws:
            self.ws.close()

        print("[deploy] Disconnected from deploy service.")
        sys.exit(0)


    def run(self, host: str) -> None:
        signal.signal(signal.SIGINT, self.signal_handler)
        # websocket.enableTrace(True)

        while True:
            try:
                self.ws = WebSocketApp(
                    host,
                    on_open=self.on_open,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                )

                self.ws.run_forever()

                self.ws = None
                print("[deploy] Reconnecting in 5 sec.")
                time.sleep(5)
            except:
                self.ws = None
                print("[deploy] Connection to deploy service closed abruptly. Reconnecting...")
                time.sleep(5)


if __name__ == "__main__":
    node_id = "admin_node1"
    host = f"ws://localhost:8300/zsvc/deploy/connect/{node_id}"

    # TODO: Save the response with an *adapter* to the appropriate location.
    # TODO: Call MainDriver with the given callback.
    def response_callback(response: DeployResponse):
        proto_adapter.adapt(response, node_id)

    def done_callback():
        print("DONE from callback")

    def cancel_callback():
        print("CANCEL from callback")

    handler = DeployHandler(
        response_callback=response_callback,
        cancel_callback=cancel_callback,
        done_callback=done_callback,
    )
    handler.run(host)
