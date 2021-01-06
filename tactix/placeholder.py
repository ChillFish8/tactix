from typing import Callable, Any


class TactixActor:
    """
    Represents the native Actor class, this should not be implemented by the
    user directly, this is instead a raw implementation for low level
    implementations, developers should instead opt to use the
    main `tactix.Actor` class which implements all the required handling of
    this class.
    """

    def __init__(self, _cb: Callable) -> None: ...

    def send(self, event: str, message: Any) -> None:
        """
        Sends a message to a actor, this will not block.

        Args:
            event:
                The name of the event callback, this should not include the
                prefixed 'on_' and simply just be the name.

                This is parameter should be a string.

            message:
                The object to be sent to the channel, this can be any object.
        """

    def send_later(self, event: str, message: Any, delay: float) -> None:
        """
        Sends a message to an actor after a given delay (float in seconds),
        this will not block and will just schedule a new task to be made.

        Args:
            event:
                The name of the event callback, this should not include the
                prefixed 'on_' and simply just be the name.

                This is parameter should be a string.

            message:
                The object to be sent to the channel, this can be any object.

            delay:
                The time to have elapsed before sending the message, time in
                seconds and can be represented as a float.
        """

    def shutdown(self) -> None:
        """
        Shuts down the actor by cancelling the pending tasks that watches
        for messages, any pending messages at the time will be destroyed.
        """


class TactixRuntime:
    """
    Represents the actor runtime built on top of Tokio's Scheduler,
    this spawns the runtime in a background thread to prevent deadlocks
    with Python's GIL.
    """
    def __init__(self) -> None: ...

    def wait(self) -> None:
        """
        Waits for the runtime worker thread to finish, this will never
        return unless `TactixRuntime.shutdown(self)` is called to begin
        shutting down the actors that will be pending.
        """

    def shutdown(self) -> None:
        """
        Begins the shutdown of the runtime, this will start to stop running
        tasks in the background and will eventually stop completely.

        NOTE:
            There is not limit / timeout of how long it will take to shutdown
            after this function is called.
        """
