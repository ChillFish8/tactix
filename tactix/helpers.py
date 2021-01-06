class OnceTick:
    def __init__(self):
        self.__state = 0

    def __await__(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.__state == 0:
            self.__state += 1
            return

        if self.__state == 1:
            self.__state += 1
            raise StopIteration(None)
        raise AssertionError("Invalid state")
