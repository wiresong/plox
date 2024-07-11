from .errors import RuntimeError


class LoxClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def arity(self):
        initializer = self.find_method("init")
        if initializer is not None:
            return initializer.arity()
        return 0

    def call(self, interpreter, args):
        instance = LoxInstance(self)
        init = self.find_method("init")
        if init is not None:
            init.bind(instance).call(interpreter, args)
        return instance


    def find_method(self, name):
        if self.methods.get(name):
            return self.methods[name]

    def __repr__(self):
        return f"<class {self.name}>"


class LoxInstance:
    def __init__(self, parent):
        self.parent = parent
        self.fields = {}


    def get(self, field):
        if self.fields.get(field.lexeme) is not None:
            return self.fields[field.lexeme]
        else:
            method = self.parent.find_method(field.lexeme)
            if method:
                return method.bind(self)
        raise RuntimeError(field, f"undefined property {field.lexeme}")

    def set(self, name, value):
        self.fields[name.lexeme] = value

    def __repr__(self):
        return f"<instance {self.parent.name}>"
