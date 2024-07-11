import sys

from .interpreter import Interpreter
from .parser import Parser
from .resolver import Resolver
from .tokenizer import Tokenizer


class Lox:
    def __init__(self):
        self.had_error = False
        self.had_runtime_error = False
        self.interpreter = Interpreter(self)

    def run_file(self, file):
        with open(file, encoding="utf-8") as f:
            self.run(f.read())
        if self.had_error:
            sys.exit(65)

    def run_prompt(self):
        while True:
            print(">")
            s = input()
            self.run(s)
            self.had_error = False
            self.had_runtime_error = False


    def run(self, s):
        tokens = Tokenizer(self, s).tokenize()
        parser = Parser(self, tokens)
        statements = parser.parse()
        if self.had_error:
            return
        if self.had_runtime_error:
            sys.exit(70)
        resolver = Resolver(self, self.interpreter)
        resolver.resolve_statements(statements)
        if self.had_error:
            return
        self.interpreter.interpret(statements)

    def error(self, line, s):
        self.had_error = True
        print(f"Error at line {line}: {s}")

    def runtime_error(self, error):
        self.had_runtime_error = True
        print(f"Runtime error at line {error.token.line}: {error}")
