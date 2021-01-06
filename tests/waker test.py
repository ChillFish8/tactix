from time import time

import tactix
from tactix import Actor, ActorContext


class MyActor(Actor):
    def __init__(self):
        super().__init__()
        self.count = 0

    @Actor.listener()
    def on_foo(self, message):
        print(message)
        # self.handle_foo(message)

    @Actor.wrap_coroutine
    async def handle_foo(self, ctx: ActorContext, message):
        print(message)
        await ctx.sleep(message[1])
        self.count += 1

        if self.count >= 100:
            print(time())


def main():
    act1 = MyActor()
    print(time())
    act1.send("foo", ("foo 1", 5))

    tactix.run_forever()


if __name__ == '__main__':
    main()
