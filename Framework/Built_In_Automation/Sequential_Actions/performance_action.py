import time
from concurrent import futures
from typing import Callable, List, Tuple


def performance_action_handler(
    data_set: List[List[str]],
    run_sequential_actions: Callable[[List[int]], None],
) -> Tuple[str, List[int]]:
    spawn_rate = 1
    timeout = 1
    time_to_run = 1
    max_workers = None
    actions_to_execute: List[int] = []

    for left, _, right in data_set:
        left, right = left.strip(), right.strip()
        if "spawn rate" in left:
            spawn_rate = int(right)
        elif "timeout" in left:
            timeout = int(right)
        elif "time to run" in left:
            time_to_run = int(right)
        elif "max workers" in left:
            max_workers = int(right)
            if max_workers <= 1:
                # max workers cannot be less than 2 otherwise we'll have a
                # deadlock
                max_workers = 2
        elif "performance action" in left:
            l, r = map(int, right.split("-"))
            actions_to_execute = [i-1 for i in range(l, r+1)]

    # result, executed_actions = Run_Sequential_Actions(data_set_list=actions_to_execute)
    # print(result, executed_actions)

    pool = futures.ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="performance_action",
    )

    future_callables = list()

    while time_to_run > 0:
        # For every "tick", we spawn the specified number of callables.
        for i in range(spawn_rate):
            future_callables.append(
                pool.submit(
                    run_sequential_actions,
                    data_set_list=actions_to_execute,
                )
            )
        time.sleep(1)
        time_to_run -= 1

    results = []
    for f in futures.as_completed(future_callables, timeout=timeout):
        results.append(f.result())

    print(results)
    return "passed", actions_to_execute
