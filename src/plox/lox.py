from .printer import Printer
from .parser import Parser
from .tokenizer import Tokenizer


class Lox:
    def __init__(self):
        self.hadError = False

    def run_file(self, file):
        with open(file, encoding="utf-8") as f:
            self.run(f)

    def run_prompt(self):
        while True:
            print(">")
            s = input()
            self.run(s)

    def run(self, s):
        # Todo reuse tokenizer
        self.hadError = False
        tokens = Tokenizer(self, s).tokenize()
        parser = Parser(self, tokens)
        expr = parser.parse()
        if self.hadError:
            return
        print(Printer().print(expr))

    def error(self, line, s):
        self.hadError = True
        print(f"Error at line {line}: {s}")
