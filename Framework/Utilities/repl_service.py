import json
import copy
import ssl
import traceback
from threading import Thread
import io
import contextlib
import sys

import websocket
import time

from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr
from Framework.MainDriverApi import send_new_variables


ws = None
connected = False
_stop = False



def _send(msg):
    global ws
    try:
        if ws is None:
            return
        if not isinstance(msg, str):
            msg = json.dumps(msg)
        ws.send(msg)
    except Exception:
        pass


def close():
    global ws, connected, _stop
    connected = False
    _stop = True
    if ws is not None:
        try:
            ws.close(status=1000, reason="Closing REPL")
        except Exception:
            pass


def on_message(ws, message):
    try:
        data = json.loads(message)
    except Exception:
        print(f"[REPL] on_message non-JSON frame ignored: {message[:120]}")
        return
    if not isinstance(data, dict) or data.get("type") != "command":
        return

    code = data.get("msg", "")
    # snapshot protected values
    protected_list = []
    protected_snapshot = {}
    pre_existing = set()
    try:
        protected_list = list(getattr(sr, "protected_variables", []) or [])
        for name in protected_list:
            if name in sr.shared_variables:
                protected_snapshot[name] = copy.deepcopy(sr.shared_variables[name])
                pre_existing.add(name)
    except Exception:
        pass
    output_text = ""
    error_text = None
    _preview = code[:200].replace("\n", "\\n")
    print("[REPL] received command:", _preview)

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            # Try eval first for expressions
            try:
                result = None
                try:
                    result = eval(code, sr.shared_variables, sr.shared_variables)
                except SyntaxError:
                    # Not an expression so execute block
                    exec(code, sr.shared_variables, sr.shared_variables)
                except NameError as ne:
                    ident = code.strip()
                    # see if single identifier referencing shared variable
                    if ident.isidentifier():
                        if ident in sr.shared_variables:
                            result = sr.shared_variables[ident]
                        else:
                            raise
                    else:
                        raise
                if result is not None:
                    print(result)
            except Exception:
                raise
        output_text = buf.getvalue().strip()
    except Exception:
        error_text = traceback.format_exc()
    finally:
        buf.close()
        print("[REPL] execution completed:", output_text)

    # restore protected values if tampered
    tampered = []
    try:
        for name in protected_list:
            if name in pre_existing:
                pre_val = protected_snapshot.get(name, None)
                if name not in sr.shared_variables or sr.shared_variables.get(name) != pre_val:
                    sr.shared_variables[name] = pre_val
                    tampered.append(name)
            else:
                # remove if did not exist before
                if name in sr.shared_variables:
                    try:
                        del sr.shared_variables[name]
                    except Exception:
                        sr.shared_variables.pop(name, None)
                    tampered.append(name)
    except Exception:
        pass

    if error_text:
        _send({"type": "error", "msg": error_text})
    else:
        # add warning line if any protected var was tampered
        if tampered:
            if output_text:
                output_text = output_text + "\n" + "\n".join(
                    f"(read-only) Reverted attempt to modify {n}" for n in tampered
                )
            else:
                output_text = "\n".join(f"(read-only) Reverted attempt to modify {n}" for n in tampered)
        _send({"type": "output", "msg": output_text})

    # republish variables back to server so UI can refresh
    try:
        send_new_variables()
    except Exception:
        pass

    # Signal completion so UI can refresh variables after execution fully finishes
    try:
        _send({"type": "output", "msg": "__done__"})
    except Exception:
        pass


def on_error(ws, error):
    print(f"[REPL] on_error: {error}")
    return


def on_close(ws=None, _a=None, _b=None):
    global connected
    connected = False
    print("[REPL] connection closed")


def on_open(ws):
    global connected
    connected = True
    print("[REPL] on_open: connected, sending status ping")
    try:
        _send({"type": "output", "msg": "__status__:node_online"})
    except Exception:
        pass


def _run_loop(url):
    global ws, _stop
    while not _stop:
        try:
            ws = websocket.WebSocketApp(
                url,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close,
            )
            ws.on_open = on_open
            
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=20, ping_timeout=10)
            
        except Exception as e:
            print(f"[REPL] exception in run loop: {e}")
        if _stop:
            break
        time.sleep(5)


def connect(url):
    global connected, _stop
    try:
        _stop = False
        print(f"[REPL] connect() invoked url={url}")
        sys.stdout.flush()
        t = Thread(target=_run_loop, args=(url,))
        t.daemon = True
        t.start()
    except Exception as outer:
        print(f"[REPL] connect() exception: {outer}")
        sys.stdout.flush()

def ping_state():
    return {"connected": connected, "ws_is_none": ws is None, "stop": _stop}
