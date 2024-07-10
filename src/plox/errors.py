class ParseError(Exception):
    pass


class RuntimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token
