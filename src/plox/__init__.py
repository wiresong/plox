import sys

from .lox import Lox


def main():
    if len(sys.argv) > 2:
        print("Usage: plox [script]")
    lox = Lox()
    if len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()
    return 0
