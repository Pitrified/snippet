import functools
import logging
import time


def timefunc(func):
    """A decorator to time a func.

    https://towardsdatascience.com/a-simple-way-to-time-code-in-python-a9a175eb0172
    """
    log_file = logging.getLogger(f"f.{__name__}.timefunc")
    log_console = logging.getLogger(f"c.{__name__}.timefunc")

    @functools.wraps(func)
    def time_closure(*args, **kwargs):
        """time_wrapper's doc string"""
        funcname = f"{__file__}{func.__name__}"
        # funcname = f"{__name__}.{func.__name__}"
        log_file.debug(f"S: {funcname}")
        log_console.debug(f"Start: {funcname}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        time_elapsed = time.perf_counter() - start
        log_file.debug(f"E: {funcname}, T: {time_elapsed:.9f} s")
        log_console.debug(f"  End: {funcname}, Time: {time_elapsed:.9f} s")
        return result

    return time_closure


def timefunc_modulename(modulename):
    """A decorator with arguments to time a func.

    https://towardsdatascience.com/a-simple-way-to-time-code-in-python-a9a175eb0172
    https://www.artima.com/weblogs/viewpost.jsp?thread=240845#decorator-functions-with-decorator-arguments
    """
    log_file = logging.getLogger(f"f.{__name__}.timefunc")
    log_console = logging.getLogger(f"c.{__name__}.timefunc")

    def inner_function(func):
        @functools.wraps(func)
        def time_closure(*args, **kwargs):
            """time_wrapper's doc string"""

            # build a more informative function name
            funcname = f"{modulename}.{func.__name__}"

            log_file.debug(f"S: {funcname}")
            log_console.debug(f"Start: {funcname}")

            start = time.perf_counter()
            result = func(*args, **kwargs)
            time_elapsed = time.perf_counter() - start

            log_file.debug(f"E: {funcname}, T: {time_elapsed:.9f} s")
            log_console.debug(f"  End: {funcname}, Time: {time_elapsed:.9f} s")

            return result

        return time_closure

    return inner_function
