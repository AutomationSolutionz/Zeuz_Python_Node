import json
import time
import websocket
import ssl
import json
import os
from threading import Thread


# Websocket connection object that runs on a different thread.
ws = None
connected = False


def send_file(data, ws):
    """Send binary data through websocket."""

    try:
        if ws is None:
            return

        ws.send(data, websocket.ABNF.OPCODE_BINARY)
    except:
        pass


def send(msg, ws):
    """Send plain text through websocket."""

    # TODO: Make this "send" method buffered so that it only sends certain
    # amount of messages at certain intervals of time. Maybe send it in a queue
    # that a background thread reads from every 1s or so.

    try:
        if ws is None:
            return

        if not isinstance(msg, str):
            msg = json.dumps(msg)

        ws.send(msg)
    except:
        pass


def log(module_info, log_level, description):
    msg = {
        "type": "log",
        "msg": {
            "module_info": module_info,
            "log_level": log_level,
            "msg": description,
        },
    }
    global ws
    send(msg, ws)


def binary(data):
    global ws
    send_file(data, ws)


def close():
    global ws
    global connected
    connected = False
    if ws != None:
        try:
            ws.close(status=1000, reason="Test Set run complete")
        except:
            pass


def on_message(ws, message):
    print("[ws] Message:\n", message)


def on_error(ws, error):
    if isinstance(error, AttributeError):
        return
    elif isinstance(error, OSError):
        # Prevent bad file descriptor error from showing
        return
    # print("[ws] Error. Connection closed\n")


def on_close(ws=None, a=None, b=None):
    global connected
    connected = False
    # print("[ws] Connection closed.")


def on_open(ws):
    global connected
    connected = True
    # print("[ws] Live Log Connection established.")


def run_ws_thread(ws):
    try:
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, )
    except:
        pass


def connect(url):
    global ws
    global connected

    # Uncomment next line for debugging.
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(url,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = on_open

    t = Thread(target=run_ws_thread, args=(ws,))
    t.start()

    # Retry for 6s with 0.3s interval.
    # for _ in range(20):
    #     if connected:
    #         break
    #     time.sleep(0.3)
