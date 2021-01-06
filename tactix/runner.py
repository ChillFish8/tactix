from typing import Callable

from . import TactixRuntime


def run(cb: Callable, *args, **kwargs):
    """
    Creates and starts the runtime, this passes any args or kwargs to
    the callback, when the callback is finished the runtime shuts down
    and waits till it is closed.

    Args:
        cb:
            The main function of your program.
        *args:
            Any args to be passed to the callback.
        **kwargs:
            Any kwargs to be passed to the callback.
    """
    rt = TactixRuntime()

    cb(*args, **kwargs)
    rt.shutdown()
    rt.wait()


def run_forever(cb: Callable, *args, **kwargs):
    """
    Creates and starts the runtime, this passes the runtime handle and
    any args or kwargs to the callback. Unlike `tactix.run()` this does NOT
    shutdown the runtime after the main loop has finished and instead waits
    until something else has called the shutdown function of the runtime handle.

    Args:
        cb:
            The main function of your program.
        *args:
            Any args to be passed to the callback.
        **kwargs:
            Any kwargs to be passed to the callback.
    """

    rt = TactixRuntime()

    cb(rt, *args, **kwargs)

    rt.wait()
