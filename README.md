# plox
Plox is a Python port of Lox, an object-oriented, single-inheritance, lexically-scoped language from [Crafting Interpreters](https://craftinginterpreters.com/).

## Running the code
Plox currently uses [Rye](https://rye.astral.sh/) as the package manager, although anything supporting pyproject.toml should work. To run the REPL, use ``rye run plox``, and to run a file, use `rye run plox <file>``. The main directory holds example.lox, which should demonstrate some of the languages' features.

## Code structure
All code files live in the src/plox directory.

- __init__.py and __main__.py: files responsible for parsing commandline arguments and setting up the main interpreter loop
- builtins.py: built-in functions, currently only clock()
- classes.py: run-time Python representations of Lox classes
- env.py: lexical environments
- Errors.py: custom errors defined by the interpreter
- expr.py: expression AST nodes
- fun.py: runtime Python representation of a Lox function object
- interpreter.py: responsible for interpreting an AST received from the parser
- lox.py: the main loop. Sets up the tokenizer, resolver, parser, and interpreter, and takes care of error handling
- parser.py: converts a list of tokens from the tokenizer into an abstract syntax tree
- resolver.py: resolves (and provides to the interpreter) the appropriate lexical scope for variables
- stmt.py: Statement AST nodes
- tokenizer.py: converts a string into a list of tokens

## The state of the code
Currently, the codebase is a straight naive translation from the book. I hope to refactor to make things more idiomatic, but this is principally a prototype, and most of my energy will be spent on Zelox: a fast, optimized bytecode interpreter for the same language.

