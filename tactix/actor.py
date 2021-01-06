import typing as t
import inspect

from traceback import print_exc

from . import TactixActor, OnceTick


class ActorListener:
    def __init__(self, cb, name):
        self._cb = cb
        self._name = name

    def as_tuple(self):
        return self._name, self

    def __call__(self, *args, **kwargs):
        return self._cb(*args, **kwargs)


class Actor:
    def __init__(self):
        self.__actor = TactixActor(self.on_message)
        self.__listeners = self._load_listeners()

        self._load_coroutines()

    def __del__(self):
        self.__actor.shutdown()

    @classmethod
    def listener(cls, name: t.Optional[str] = None):
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
    def check_listener(cb) -> bool:
        return isinstance(cb, ActorListener)

    def _load_listeners(self):
        listeners = inspect.getmembers(self, self.check_listener)
        return dict(map(lambda parts: parts[1].as_tuple(), listeners))

    @staticmethod
    def check_coroutine(cb) -> bool:
        return isinstance(cb, CoroutineStateMachine)

    def _load_coroutines(self):
        listeners: t.List[t.Tuple[str, CoroutineStateMachine]] = inspect.getmembers(
            self,
            self.check_coroutine
        )
        for _, caller in listeners:
            caller._set_actor(actor=self)

    def on_message(self, event: str, message: t.Any):
        try:
            self.__listeners[event](self, message)
        except Exception as _:
            print_exc()

    def shutdown(self):
        self.__actor.shutdown()

    def send(self, event: str, message: t.Any, delay: float = 0):
        if delay == 0:
            self.__actor.send(event, message)
        else:
            self.__actor.send_later(event, message, delay)

    @classmethod
    def wrap_coroutine(cls, cb) -> "CoroutineStateMachine":
        return CoroutineStateMachine(cb)


class CoroutineStateMachine:
    def __init__(self, cb: t.Callable):
        self._cb = cb
        self._actor: t.Optional[Actor] = None

    def _set_actor(self, actor: Actor):
        self._actor = actor

    def __call__(self, *args, **kwargs):
        return ActorContext(self._cb, self._actor, args, kwargs)


class ActorContext(Actor):
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
        self.send("wake", None, delay=n)
        return OnceTick()
