from time import sleep

import tactix
from tactix import Actor, ActorContext


class MyActor(Actor):
    def __init__(self):
        super().__init__()
        self.count = 0

    @Actor.listener()
    def on_foo(self, message):
        self.handle_foo(message)

    @Actor.wrap_coroutine
    async def handle_foo(self, ctx: ActorContext, message):
        await ctx.sleep(message[1])
        print("done!")

    @Actor.listener(name="on_hello")
    def custom_name(self, message):
        print(f"Got: {message}")


def main():
    act1 = MyActor()
    act1.send("foo", ("foo 1", 5), delay=2)
    act1.send("hello", "Hello, World!")

    sleep(8)


if __name__ == '__main__':
    tactix.run(main)
