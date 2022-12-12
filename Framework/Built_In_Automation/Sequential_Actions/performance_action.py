import time
from concurrent import futures
from typing import Callable, List, Tuple


class LoadShape:
    def __init__(self, callback: Callable[[], None]):
        self.callback = callback


    def tick(self):
        pass


class CycleLoadShape(LoadShape):
    def __init__(self, callback: Callable[[], None], number_of_cycles=0, step_increment=1, ramp=None):
        self.callback = callback
        self.number_of_cycles = number_of_cycles
        self.step_increment = step_increment
        self.ramp = ramp


    def run(self):
        cycle = 0
        while cycle < self.number_of_cycles:
            cycle += 1


    def tick(self):
        self.callback()


def performance_action_handler(
    data_set: List[List[str]],
    run_sequential_actions: Callable[[List[int]], None],
) -> Tuple[str, List[int]]:
    number_of_cycles = 0
    step_increment = 1
    ramp = None
    max_workers = None
    actions_to_execute: List[int] = []

    for left, _, right in data_set:
        left, right = left.strip(), right.strip()
        if "number of cycles" in left:
            number_of_cycles = int(right)
        elif "step_increment" in left:
            step_increment = int(right)
        elif "ramp" in left:
            ramp = right.strip()
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
    for f in futures.as_completed(future_callables):
        results.append(f.result())

    print(results)
    return "passed", actions_to_execute
