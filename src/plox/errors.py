class ParseError(Exception):
    pass


class RuntimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token

# Not exactly an error, just a way to jump out of a deep call stack
class ReturnError(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value
