import time
import threading
import inspect
from concurrent import futures
from typing import Callable, List, Tuple, Union, Any
from Framework.Built_In_Automation.Shared_Resources import BuiltInFunctionSharedResources as sr

from Framework.Utilities import CommonUtil


MODULE_NAME = "time_base_performance_action"
zeuz_run_time = -1 #zeuz_cycle = -1
start_time = time.time()
class LoadShape:
    def run(self):
        raise Exception("this method needs to be called from one of its sub-classes")


    def tick(self, cycle, launch_count):
        raise Exception("this method needs to be called from one of its sub-classes")


class TimeLoadShape(LoadShape):
    def __init__(self, callback: Callable[[int, int], None], time_to_run=0, spawn_rate=1, timeout=1, ramp: Union[str, None]=None):
        self.callback = callback
        self.time_to_run = time_to_run
        self.spawn_rate = spawn_rate
        self.timeout = timeout

        if ramp:
            self.ramp_list = [
                float(i.strip().replace('%', '')) / 100
                for i in ramp.split(',')
            ]
        else:
            self.ramp_list = []

        # convert to set so that we remove duplicates of 0.0 and 1.0 if present
        self.ramp_list = sorted(list(set([0.0, *self.ramp_list, 1.0])))


    def _cycle_ramp(self, cycle: int):
        percentage = cycle / self.number_of_cycles
        for i in range(0, len(self.ramp_list)-1):
            rp_i = self.ramp_list[i]
            rp_i1 = self.ramp_list[i+1]
            if rp_i <= percentage <= rp_i1:
                return -1 if i % 2 == 1 else 1
        return 1


def time_base_performance_action_handler(
    data_set: List[List[str]],
    run_sequential_actions: Callable[[List[int]], None],
    timestamp_func: Callable[[], str],
) -> Tuple[str, List[int]]:
    spawn_rate = 1
    max_user = 1
    timeout = 1
    time_to_run = 1
    max_workers = None
    actions_to_execute: List[int] = []
    max_parallel_thread_count = 0
    alive_task_count = 0

    for left, _, right in data_set:
        left, right = left.strip(), right.strip()
        if "spawn rate" in left:
            if right.strip().startswith("%|"):
                spawn_rate = int(sr.get_previous_response_variables_in_strings(right.strip()))
            else:
                spawn_rate = int(right)
        elif "max user" in left:
            if right.strip().startswith("%|"):
                max_user = int(sr.get_previous_response_variables_in_strings(right.strip()))
            else:
                max_user = int(right)
        elif "timeout" in left:
            if right.strip().startswith("%|"):
                timeout = int(sr.get_previous_response_variables_in_strings(right.strip()))
            else:
                timeout = int(right)
        elif "time to run" in left:
            if right.strip().startswith("%|"):
                time_to_run = int(sr.get_previous_response_variables_in_strings(right.strip()))
            else:
                time_to_run = int(right)
            time_to_run = time_to_run + int(time.time())
        elif "max workers" in left:
            if right.strip().startswith("%|"):
                max_workers = int(sr.get_previous_response_variables_in_strings(right.strip()))
            else:
                max_workers = int(right)
            if max_workers <= 1:
                # max workers cannot be less than 2 otherwise we'll have a
                # deadlock
                max_workers = 2
        elif "time base performance action" in left:
            if right.strip().startswith("%|"):
                right = sr.get_previous_response_variables_in_strings(right.strip())
                
            action_ranges = right.split(',')
            
            actions_to_execute=[]
            for action_range in action_ranges:
                action_range=action_range.split('-') #[5-7] to [5,7], [5] to [5] if no '-' present
                if len(action_range) == 1:
                    actions_to_execute.append(int(action_range[0].strip())-1)
                else:
                    l, r = map(int, action_range) #[9,14] to l=9 and r=14
                    for i in range(l, r+1):
                        actions_to_execute.append(i-1) #[9,10,11,12,13,14]

    # result, executed_actions = Run_Sequential_Actions(data_set_list=actions_to_execute)
    # print(result, executed_actions)
    
    
    def task():
        """
        A task represents a single thread of execution/user journey and contains
        performance related information.
        """
        nonlocal alive_task_count, max_parallel_thread_count
        alive_task_count += 1
        max_parallel_thread_count = max(max_parallel_thread_count, threading.active_count())

        timestamp = timestamp_func()
        start_time = time.perf_counter_ns()
        result = run_sequential_actions(actions_to_execute)
        end_time = time.perf_counter_ns()
        alive_task_count -= 1
        print('-----------------------------------')
        print(result)
        print('-----------------------------------')
        

        max_parallel_thread_count = max(max_parallel_thread_count, threading.active_count())

        return (result[0] == "passed", timestamp, end_time - start_time)
    

    pool = futures.ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix="time_base_performance_action",
    )

    future_callables = list()

    while time_to_run > time.time():
        # For every "tick", we spawn the specified number of callables.
        if max_user > alive_task_count:
            for i in range(min(max_user-alive_task_count, spawn_rate)):
                future_callables.append(
                    pool.submit(
                        task
                    )
                )
            time.sleep(1)

    results = []
    for f in futures.as_completed(future_callables, timeout=timeout):
        results.append(f.result())

    # print(results)
    return "passed", actions_to_execute, results
