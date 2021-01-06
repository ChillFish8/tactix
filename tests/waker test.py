import tactix
from tactix import Actor, ActorContext


class MyActor(Actor):
    def __init__(self):
        super().__init__()
        self.count = 0

    @Actor.listener()
    def on_foo(self, message):
        print(message)
        self.handle_foo(message)

    @Actor.wrap_coroutine
    async def handle_foo(self, ctx: ActorContext, message):
        await ctx.sleep(message[1])
        print("done!")


def main():
    act1 = MyActor()
    act1.send("foo", ("foo 1", 5), delay=2)
    act1.send("foo", ("foo 1", 5), delay=2)
    tactix.run_forever()


if __name__ == '__main__':
    main()
