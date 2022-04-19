# Author: sazid

import websocket
import rel
import threading
import sys
from pathlib import Path
sys.path.append(str(Path.cwd() / "Framework" / "pb" / "v1"))

# from Framework.pb.v1 import deploy_response_message_pb2
from pb.v1 import deploy_response_message_pb2
# from Framework.Utilities import CommonUtil



COMMAND_DONE = "DONE"
COMMAND_CANCEL = "CANCEL"
COMMAND_NEXT = "NEXT"


def on_message(ws, message):
    print("[deploy] Message received")

    if message == COMMAND_DONE:
        # We're done for this session. Send NEXT command to wait for next items
        # to become available.
        print("[deploy] Run complete.")
        return

    elif message == COMMAND_CANCEL:
        # Cancel runid
        print("[deploy] Run cancelled.")
        # CommonUtil.run_cancelled = True
        return

    response = deploy_response_message_pb2.DeployResponse()
    response.ParseFromString(message)
    print(response)

    ws.send(COMMAND_NEXT)

def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    print(close_status_code, close_msg)
    ws.send(COMMAND_NEXT)

def on_open(ws):
    print("[deploy] Connected to streaming deploy service.")
    ws.send(COMMAND_NEXT)

if __name__ == "__main__":
    while True:
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp("ws://localhost:8300/zsvc/deploy/connect/admin_node1",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

        ws.run_forever(dispatcher=rel)  # Set dispatcher to automatic reconnection
        rel.signal(2, rel.abort)  # Keyboard Interrupt
        rel.dispatch()
