"""
Verbose startup/request logging for diagnosing hangs.

Activated by `python node_cli.py --verbose-log`.
Prints timestamped entry/exit with duration for:
  - Startup functions called from main()
  - Every HTTP request made through RequestFormatter
"""

import time
import functools
from contextlib import contextmanager
from datetime import datetime, timezone

VERBOSE = False


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def vlog(msg: str) -> None:
    if VERBOSE:
        print(f"[VERBOSE {_ts()}] {msg}")


@contextmanager
def vtimed(label: str):
    """Context manager that logs entry/exit/duration of a block."""
    if not VERBOSE:
        yield
        return
    print(f"[VERBOSE {_ts()}] >> ENTER  {label}")
    t0 = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - t0
        print(f"[VERBOSE {_ts()}] << EXIT   {label}  ({elapsed:.3f}s)")


def vtimed_func(label: str | None = None):
    """Decorator that logs function entry/exit/duration when VERBOSE is on."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            name = label or fn.__qualname__
            if not VERBOSE:
                return fn(*args, **kwargs)
            print(f"[VERBOSE {_ts()}] >> ENTER  {name}")
            t0 = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - t0
                print(f"[VERBOSE {_ts()}] << EXIT   {name}  ({elapsed:.3f}s)")
        return wrapper
    return decorator


def vtimed_async(label: str | None = None):
    """Async version of vtimed_func."""
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            name = label or fn.__qualname__
            if not VERBOSE:
                return await fn(*args, **kwargs)
            print(f"[VERBOSE {_ts()}] >> ENTER  {name}")
            t0 = time.perf_counter()
            try:
                return await fn(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - t0
                print(f"[VERBOSE {_ts()}] << EXIT   {name}  ({elapsed:.3f}s)")
        return wrapper
    return decorator
