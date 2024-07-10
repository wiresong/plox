import time


class Clock:
    def arity(self):
        return 0

    def call(self, interpreter, args):
        return int(time.time())
