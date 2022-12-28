import time
from concurrent import futures
from typing import Callable, List, Tuple, Literal, Union, Any


class LoadShape:
    def run(self):
        raise Exception("this method needs to be called from one of its sub-classes")


    def tick(self, cycle, launch_count):
        raise Exception("this method needs to be called from one of its sub-classes")


class CycleLoadShape(LoadShape):
    def __init__(self, callback: Callable[[int, int], None], number_of_cycles=0, step_increment=1, ramp: Union[str, None]=None):
        self.callback = callback
        self.number_of_cycles = number_of_cycles
        self.step_increment = step_increment

        if ramp:
            self.ramp_list = [
                float(i.strip().replace('%', '')) / 100
                for i in ramp.split(',')
            ]
        else:
            self.ramp_list = []

        # convert to set so that we remove duplicates of 0.0 and 1.0 if present
        self.ramp_list = sorted(list(set([0.0, *self.ramp_list, 1.0])))


    def _cycle_ramp(self, cycle: int) -> Literal[-1, 1]:
        percentage = cycle / self.number_of_cycles
        for i in range(0, len(self.ramp_list)-1):
            rp_i = self.ramp_list[i]
            rp_i1 = self.ramp_list[i+1]
            if rp_i <= percentage <= rp_i1:
                return -1 if i % 2 == 1 else 1
        return 1


    def run(self):
        # current cycle count
        cycle = 0
        # number of threads to launch per cycle
        launch_count = 0

        # loop until the target number of cycles are executed
        while cycle < self.number_of_cycles:
            launch_count = launch_count + (self.step_increment * self._cycle_ramp(cycle))
            # never let the launch count fall below zero
            if launch_count <= 0:
                launch_count = self.step_increment

            # this is going to block the loop and let the tick handler decide
            # when to move on to the next iteration
            self.tick(cycle, launch_count)

            cycle += 1


    def tick(self, cycle: int, launch_count: int):
        self.callback(cycle, launch_count)


def performance_action_handler(
    data_set: List[List[str]],
    run_sequential_actions: Callable[[List[int]], Tuple[str, List[int]]],
    timestamp_func: Callable[[], str],
) -> Tuple[str, List[int], List[Any]]:
    number_of_cycles = 0
    step_increment = 1
    ramp = None
    max_workers = None
    actions_to_execute: List[int] = []

    for left, _, right in data_set:
        left, right = left.strip(), right.strip()
        if "number of cycles" in left:
            number_of_cycles = int(right)
        elif "step increment" in left:
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
            action_ranges=right.split(',') # 5-7,8,9-14 to [5-7,8,9-14]
            actions_to_execute=[]
            for action_range in action_ranges:
                action_range=action_range.split('-') #[5-7] to [5,7], [5] to [5] if no '-' present
                if len(action_range)==1:
                    actions_to_execute.append(int(action_range[0].strip())-1)
                else:
                    l,r=action_range #[9,14] to l=9 and r=14
                    for i in range(l,r+1):
                        actions_to_execute.append(i-1) #[9,10,11,12,13,14]

    # result, executed_actions = Run_Sequential_Actions(data_set_list=actions_to_execute)
    # print(result, executed_actions)

    pool = futures.ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="performance_action",
    )

    def task(cycle):
        """
        A task represents a single thread of execution/user journey and contains
        performance related information.
        """
        timestamp = timestamp_func()
        start_time = time.perf_counter_ns()
        result = run_sequential_actions(actions_to_execute)
        end_time = time.perf_counter_ns()
        return (result[0] == "passed", timestamp, end_time - start_time, cycle)


    results = []
    def tick_handler(cycle: int, launch_count: int):
        future_callables = list()
        for _ in range(launch_count):
            future_callables.append(
                pool.submit(task, cycle=cycle),
            )

        # wait for a cycle to complete by waiting on all the submitted tasks
        for f in futures.as_completed(future_callables):
            results.append(f.result())


    load_shape = CycleLoadShape(
        callback=tick_handler,
        number_of_cycles=number_of_cycles,
        step_increment=step_increment,
        ramp=ramp,
    )

    load_shape.run()

    return "passed", actions_to_execute, results
