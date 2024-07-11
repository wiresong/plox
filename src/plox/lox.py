import sys

from .interpreter import Interpreter
from .parser import Parser
from .printer import Printer
from .resolver import Resolver
from .tokenizer import Tokenizer


class Lox:
    def __init__(self):
        self.hadError = False
        self.hadRuntimeError = False
        self.interpreter = Interpreter(self)

    def run_file(self, file):
        with open(file, encoding="utf-8") as f:
            self.run(f.read())

    def run_prompt(self):
        while True:
            self.hadError = False
            self.hadRuntimeError = False
            print(">")
            s = input()
            self.run(s)

    def run(self, s):
        # Todo reuse tokenizer
        tokens = Tokenizer(self, s).tokenize()
        parser = Parser(self, tokens)
        statements = parser.parse()
        if self.hadError:
            return
        if self.hadRuntimeError:
            sys.exit(70)
        resolver = Resolver(self, self.interpreter)
        resolver.resolve_statements(statements)
        if self.hadError:
            return
        self.interpreter.interpret(statements)

    def error(self, line, s):
        self.hadError = True
        print(f"Error at line {line}: {s}")

    def runtime_error(self, error):
        self.hadRuntimeError = True
        print(f"Error with token {error.token}: {error}")
