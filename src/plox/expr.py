class Expr:
    pass


# This is just a convenience method which allows us to elide full class definitions
# The first argument is the class name, and the remaining arguments are the parameters that the class takes
# The function generates a class accepting those parameters, as well as an accept method for the visitor pattern
def _makeclass(*args1):
    def init(self, *args2):
        super(Expr, self).__init__()
        for key, value in zip(args1[1:], args2):
            setattr(self, key, value)

    def accept(self, visitor):
        funcname = f"visit_{args1[0].lower()}"
        return getattr(visitor, funcname)(self)

    return type(args1[0], (Expr,), {"__init__": init, "accept": accept})


Assign = _makeclass("Assign", "name", "value")
Binary = _makeclass("Binary", "left", "operator", "right")
Grouping = _makeclass("Grouping", "expression")
Literal = _makeclass("Literal", "value")
Logical = _makeclass("Logical", "left", "operator", "right")
Unary = _makeclass("Unary", "operator", "right")
Variable = _makeclass("Variable", "name")
