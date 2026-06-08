import time
import functools
import inspect
from . import CommonUtil
from Framework.Utilities.CommonUtil import failed_tag_list


def _log_custom_fail_message(result, args):
    custom_fail_message = ""
    if isinstance(result, str) and result in failed_tag_list:
        try:
            for row in args[0]:
                if row[1].replace(" ", "").lower() == "failmessage":
                    custom_fail_message = row[2]
            # Todo: print the custom_fail_message
            if custom_fail_message:
                CommonUtil.ExecLog(None, custom_fail_message, 3)
        except:
            pass


def _log_function_exit(func_name, start_time):
    end_time = time.perf_counter()
    run_time = end_time - start_time

    CommonUtil.ExecLog(
        None,
        f"Exited from function: {func_name!r}. Runtime: {run_time:.4f} secs.",
        5,
    )


def logger(func):
    """Log the entry and exit of the decorated function"""

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            CommonUtil.ExecLog(None, f"Entering into function: {func.__name__!r}.", 5)
            result = await func(*args, **kwargs)
            _log_custom_fail_message(result, args)
            _log_function_exit(func.__name__, start_time)

            return result

        return async_wrapper

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        CommonUtil.ExecLog(None, f"Entering into function: {func.__name__!r}.", 5)
        result = func(*args, **kwargs)
        _log_custom_fail_message(result, args)
        _log_function_exit(func.__name__, start_time)

        return result

    return wrapper


def deprecated(func):
    """Used to denote that a function has been deprecated."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        CommonUtil.ExecLog(
            None,
            f"The function {func.__name__!r} has been deprecated and will be removed at a later period.",
            2,
        )
        return func(*args, **kwargs)

    return wrapper
