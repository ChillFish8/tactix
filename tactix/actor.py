import typing as t
import inspect

from traceback import print_exc

from . import TactixActor, OnceTick


class ActorListener:
    """
    Wraps a function / callable to become a message handler, if a event is
    emitted of the given name of the function (not including the 'on_'), the
    listener is called with the given message.
    """
    def __init__(self, cb, name):
        self._cb = cb
        self._name = name

    def as_tuple(self):
        return self._name, self

    def __call__(self, *args, **kwargs):
        return self._cb(*args, **kwargs)


class Actor:
    """
    The main actor class that all actors should inherit from, this implements
    the necessary handlers for the runtime and managers.
    """

    def __init__(self):
        self.__actor = TactixActor(self.on_message)
        self.__listeners = self._load_listeners()

        self._load_coroutines()

    def __del__(self):
        self.__actor.shutdown()

    @classmethod
    def listener(cls, name: t.Optional[str] = None):
        """
        Wraps a function or callable, adding it to the actor handle so that
        it is invoked when a message is sent to the actor and has the relevant
        event name.

        Args:
            name:
                A optional name to give to the listener if you wish to name
                it something other than the function name. e.g. to avoid naming
                collisions.
        """

        def wrapper(func):
            if name is None:
                name_ = func.__name__
            else:
                name_ = name

            if not name_.startswith("on_"):
                raise ValueError("Event names must be prefixed with 'on_'.")

            if " " in name_:
                raise ValueError("Event names must not contain spaces.")

            return ActorListener(func, name_[3:])

        return wrapper

    @staticmethod
    def _check_listener(cb) -> bool:
        return isinstance(cb, ActorListener)

    def _load_listeners(self):
        listeners = inspect.getmembers(self, self._check_listener)
        return dict(map(lambda parts: parts[1].as_tuple(), listeners))

    @staticmethod
    def _check_coroutine(cb) -> bool:
        return isinstance(cb, CoroutineStateMachine)

    def _load_coroutines(self):
        listeners: t.List[t.Tuple[str, CoroutineStateMachine]] = inspect.getmembers(
            self,
            self._check_coroutine
        )
        for _, caller in listeners:
            caller._set_actor(actor=self)

    def on_message(self, event: str, message: t.Any):
        """
        The base call where all events to the actor are sent to, the handler
        then invokes the relevant handle.
        """
        try:
            self.__listeners[event](self, message)
        except Exception as _:
            print_exc()

    def shutdown(self):
        """ Shuts down the actor and its relevant waiters """
        self.__actor.shutdown()

    def send(self, event: str, message: t.Any, delay: float = 0):
        """
        Sends a message to this actor. This will never block.
        If a delay is given (float in seconds), the message will send
        after the time has elapsed.

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
        if delay == 0:
            self.__actor.send(event, message)
        else:
            self.__actor.send_later(event, message, delay)

    @classmethod
    def wrap_coroutine(cls, cb) -> "CoroutineStateMachine":
        """ Wraps a coroutine to become a finite state machine """
        return CoroutineStateMachine(cb)


class CoroutineStateMachine:
    """
    Turns a coroutine into a state machine producer. The coroutine is polled
    and state changed when a actor invokes a wakeup.
    """

    def __init__(self, cb: t.Callable):
        self._cb = cb
        self._actor: t.Optional[Actor] = None

    def _set_actor(self, actor: Actor):
        self._actor = actor

    def __call__(self, *args, **kwargs):
        return ActorContext(self._cb, self._actor, args, kwargs)


class ActorContext(Actor):
    """
    Used to handle the context of a given coroutine state machine
    this manages the coroutine state and also suspension via the sleep function
    """

    def __init__(self, cb: t.Callable, actor: Actor, args, kwargs):
        super().__init__()
        self._coroutine = cb(
            actor,
            self,
            *args,
            **kwargs
        ).__await__().__iter__()

        self._start()

    def _start(self):
        self.send("wake", None)

    @Actor.listener()
    def on_wake(self, _):
        try:
            next(self._coroutine)
        except StopIteration:
            self.shutdown()

    def sleep(self, n: float):
        """
        Suspends the running coroutine without blocking the rest of the worker
        thread, you can use time.sleep(n) however this will take a worker
        thread out of action for the time.
        """
        self.send("wake", None, delay=n)
        return OnceTick()
