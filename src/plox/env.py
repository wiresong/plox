from .errors import RuntimeError


class Env:
    def __init__(self, enclosing=None):
        self.enclosing = enclosing
        self.dict = {}

    def define(self, name, value):
        self.dict[name] = value

    def assign(self, name, value):
        if name.lexeme in self.dict:
            self.dict[name.lexeme] = value
        elif self.enclosing is not None:
            self.enclosing.assign(name, value)
        else:
            raise RuntimeError(name, f"Undefined variable {name.lexeme}")

    def get(self, name):
        if name.lexeme in self.dict:
            return self.dict[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)

        raise RuntimeError(name, f"Attempt to access undefined variable {name.lexeme}")

    def get_at(self, distance, name):
        env = self.ancestor(distance)
        return env.dict[name]

    def assign_at(self, distance, name, value):
        env = self.ancestor(distance)
        env.dict[name] = value

    def ancestor(self, distance):
        env = self
        for _ in range(distance):
            env = env.enclosing
        return env
    