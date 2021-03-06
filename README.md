# Tactix
A work-stealing actor framework for Python built on Tokio.rs.

The easiest way to understand how Tactix works is think: 
#### asyncio + threading + actors => tactix

Unlike asyncio tactix will not be stopped or be interrupted by blocking tasks,
instead if a particular worker thread is blocking the other threads will steal
the work off of the blocked thread until it is released again. 

This does mean you can use regular blocking calls like time.sleep(n) and not
fear blocking the whole loop but note this will still affect the loop if more
than `n` blocking tasks are running where `n` is the amount of logical CPU cores.

## Example
```py
from time import sleep

import tactix
from tactix import Actor, ActorContext


class MyActor(Actor):
    def __init__(self):
        super().__init__()

    @Actor.listener()
    def on_foo(self, message):
        self.handle_foo(message)

    @Actor.wrap_coroutine
    async def handle_foo(self, ctx: ActorContext, message):
        # Like asyncio, using a non-blocking sleep, thousands of
        # tasks can run on a single thread.
        await ctx.sleep(message[1])
        print("done!")

    @Actor.listener(name="on_hello")
    def custom_name(self, message):
        # Now this will block the worker but all other tasks will be 
        # un-effected as the work stealer will have re-distributed tasks.
        sleep(2)
        print(f"Got: {message}")


def main():
    act1 = MyActor()
    act1.send("foo", ("foo 1", 5), delay=2)
    act1.send("hello", "Hello, World!")

    sleep(8)


if __name__ == '__main__':
    tactix.run(main)
```


## Building

Obviously because this system is built of the Rust back bone you're going to need
to install Rust, you will also need `cmake`.

### Using Maturin:

1) `git pull https://github.com/ChillFish8/tactix.git`

2) `maturin develop` or `maturin develop --release`

3) Have fun.

