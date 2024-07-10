from .errors import ReturnError
from .env import Env


class Fun:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, args):
        env = Env(self.closure)
        for (param, arg) in zip(self.declaration.params, args):
            env.define(param.lexeme, arg)
        try:
            interpreter.eval_block(self.declaration.body, env)
        except ReturnError as e:
            return e.value

    def __repr__(self):
        return f"<fn {self.declaration.name}>"

