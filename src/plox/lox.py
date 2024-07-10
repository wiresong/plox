import sys

from .interpreter import Interpreter
from .printer import Printer
from .parser import Parser
from .tokenizer import Tokenizer


class Lox:
    def __init__(self):
        self.hadError = False
        self.hadRuntimeError = False
        self.interpreter = Interpreter(self)

    def run_file(self, file):
        with open(file, encoding="utf-8") as f:
            self.run(f)

    def run_prompt(self):
        while True:
            self.hadError = False
            print(">")
            s = input()
            self.run(s)

    def run(self, s):
        # Todo reuse tokenizer
        tokens = Tokenizer(self, s).tokenize()
        parser = Parser(self, tokens)
        expr = parser.parse()
        if self.hadError:
            return
        if self.hadRuntimeError:
            sys.exit(70)
        self.interpreter.interpret(expr)

    def error(self, line, s):
        self.hadError = True
        print(f"Error at line {line}: {s}")

    def runtime_error(self, error):
        self.hadRuntimeError = True
        print(f"Error with token {error.token}: {error}")
