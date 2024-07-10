class Stmt:
    pass


# This is just a convenience method which allows us to elide full class definitions
# The first argument is the class name, and the remaining arguments are the parameters that the class takes
# The function generates a class accepting those parameters, as well as an accept method for the visitor pattern
def _makeclass(*args1):
    def init(self, *args2):
        super(Stmt, self).__init__()
        for key, value in zip(args1[1:], args2):
            setattr(self, key, value)

    def accept(self, visitor):
        funcname = f"visit_{args1[0].lower()}"
        return getattr(visitor, funcname)(self)

    return type(args1[0], (Stmt,), {"__init__": init, "accept": accept})

Block = _makeclass("Block", "statements")
Expression = _makeclass("Expression", "expr")
Function = _makeclass("Function", "name", "params", "body")
If = _makeclass("If", "condition", "thenbranch", "elsebranch")
Print = _makeclass("Print", "expr")
Return = _makeclass("Return", "keyword", "value")
Var = _makeclass("Var", "name", "initializer")
While = _makeclass("While", "condition", "body")
