"""Tracks action worker threads that are still running after their action_timeout.

Python cannot kill a thread. When an action exceeds action_timeout, the node
stops waiting for it and moves on, but the thread keeps running. If it never
finishes, it keeps holding whatever it was blocked on, and those threads pile
up across runs. The node checks `stuck_threads()` after each run and restarts
itself when any are left (see node_cli.py).
"""

import threading

_lock = threading.Lock()
_workers = []


def track_timed_out_worker(worker):
    """Remember a worker whose action exceeded action_timeout.

    `worker` must provide a `thread` attribute and an `is_stuck()` method that
    returns True while it is still running a timed-out action.
    """
    with _lock:
        if all(worker is not w for w in _workers):
            _workers.append(worker)


def stuck_threads():
    """Return the threads that are still running an action that timed out."""
    with _lock:
        stuck = [w for w in _workers if w.thread.is_alive() and w.is_stuck()]
        # Forget workers that finished; a worker that gets stuck again is
        # tracked again on its next timeout.
        _workers[:] = stuck
    return [w.thread for w in stuck]


def restart_cli_args(parsed):
    """Command line arguments for restarting the node in its running mode.

    `parsed` is the node_cli argparse result. Credentials (-s/-k) and --logout
    are left out on purpose: the saved settings already hold the current
    credentials, which may have been changed since startup (e.g. from the
    local server), and must not be reset. One-off commands (key management,
    -ild) never reach a run, so they are not relevant here.
    """
    args = []
    if parsed.node_id:
        args += ["-n", parsed.node_id]
    if parsed.max_run_history:
        args += ["-m", parsed.max_run_history]
    if parsed.log_dir:
        args += ["-d", parsed.log_dir]
    if parsed.gh_token:
        args += ["-gh", parsed.gh_token]
    if parsed.stop_pip_auto_update:
        args.append("-spu")
    if parsed.show_browser_log:
        args.append("-sbl")
    if parsed.stop_live_log:
        args.append("-slg")
    if parsed.chrome_fetch is not None:
        args += ["-cf", str(parsed.chrome_fetch)]
    if parsed.chrome_cleanup is not None:
        args += ["-cc", str(parsed.chrome_cleanup)]
    if parsed.disable_mobile_install:
        args.append("--disable-mobile-install")
    return args


def restart_command(executable, orig_argv, argv, script, cli_args):
    """Full argv to re-run the node: same interpreter, interpreter options and script."""
    interpreter_options = orig_argv[1 : len(orig_argv) - len(argv)]
    return [executable, *interpreter_options, script, *cli_args]
