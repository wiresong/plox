class Printer:
    def print(self, expr):
        return expr.accept(self)

    def parenthesize(self, name, *exprs):
        s = f"({name} "
        for expr in exprs:
            s += f"{expr.accept(self)} "
        s += ")"
        return s

    def visit_binary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal(self, expr):
        return "nil" if expr.value is None else expr.value

    def visit_unary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)
