# Author: sazid

# import websocket
import time
from urllib import response
from websocket import WebSocketApp
from typing import Callable
import threading
from concurrent.futures import ThreadPoolExecutor
import signal
from pathlib import Path

import sys
# Uncomment the following lines for single-file debug
# sys.path.append(str(Path.cwd() / "Framework" / "pb" / "v1"))
# from pb.v1.deploy_response_message_pb2 import DeployResponse

# Comment the following line for single-file debug
from Framework.pb.v1.deploy_response_message_pb2 import DeployResponse



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
        done_callback: Callable[[None], bool],
    ) -> None:
        self.ws = None
        self.quit = False
        self.response_callback = response_callback
        self.cancel_callback = cancel_callback

        # Done callback should return true if node does not want to run anymore
        # test cases, false otherwise.
        self.done_callback = done_callback

        self.backoff_time = 0
        # self.thread_pool = ThreadPoolExecutor(max_workers=1)


    def on_message(self, ws: WebSocketApp, message) -> None:
        if message == self.COMMAND_DONE:
            # We're done for this run session.
            self.quit = self.done_callback()
            return

        elif message == self.COMMAND_CANCEL:
            # Run cancelled by the user/service.
            self.cancel_callback()
            return

        self.response_callback(message)
        # self.thread_pool.submit(self.response_callback, message)
        ws.send(self.COMMAND_NEXT)


    def on_error(self, ws: WebSocketApp, error) -> None:
        print("[deploy] Error communicating with the deploy service.")
        print(error)
        if self.backoff_time < 6:
            self.backoff_time += 1


    def on_close(self, ws: WebSocketApp, close_status_code: int, close_msg) -> None:
        print("[deploy] Connection closed.")
        pass


    def on_open(self, ws: WebSocketApp) -> None:
        # on successful connection, reset backoff time
        self.backoff_time = 0

        print("[deploy] Connected to deploy service.")
        ws.send(self.COMMAND_NEXT)


    def signal_handler(self, sig, frame):
        print("[deploy] Received interrupt signal (Ctrl-C), disconnecting from service...")
        self.quit = True
        self.cancel_callback()

        if self.ws:
            self.ws.close()

        # print("[deploy] Disconnected from deploy service.")
        sys.exit(0)


    def run(self, host: str) -> None:
        signal.signal(signal.SIGINT, self.signal_handler)
        # websocket.enableTrace(True)

        while not self.quit:
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

                print(f"[deploy] Establishing connection in {1 << self.backoff_time} secs...")
                time.sleep(1 << self.backoff_time)

            except:
                self.ws = None
                print(f"[deploy] Connection to deploy service closed abruptly. Reconnecting in {1 << self.backoff_time} secs...")
                time.sleep(1 << self.backoff_time)


if __name__ == "__main__":
    from Framework.deploy_handler import proto_adapter

    node_id = "admin_node1"
    host = f"ws://localhost:8300/zsvc/deploy/connect/{node_id}"

    # TODO: Save the response with an *adapter* to the appropriate location.
    # TODO: Call MainDriver with the given callback.
    def response_callback(response: str):
        node_json = proto_adapter.adapt(response, node_id)
        print(node_json[0]["run_id"])

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
