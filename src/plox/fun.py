from .env import Env
from .errors import ReturnError


class Fun:
    def __init__(self, declaration, closure, is_initializer):
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self):
        return len(self.declaration.params)

    def call(self, interpreter, args):
        env = Env(self.closure)
        for (param, arg) in zip(self.declaration.params, args):
            env.define(param.lexeme, arg)
        try:
            interpreter.eval_block(self.declaration.body, env)
        except ReturnError as e:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return e.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

    def bind(self, instance):
        env = Env(self.closure)
        env.define("this", instance)
        return Fun(self.declaration, env, self.is_initializer)

    def __repr__(self):
        return f"<fn {self.declaration.name}>"

