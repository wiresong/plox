class Printer:
    def print(self, expr):
        return expr.accept(self)

    def parenthesize(self, name, *exprs):
        s = f"({name} "
        for expr in exprs:
            s += f"{expr.accept(self)} "
        s += ")"
        return s

    def visitBinary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGrouping(self, expr):
        return self.parenthesize("group", expr.expression)

    def visitLiteral(self, expr):
        return "nil" if expr.value is None else expr.value

    def visitUnary(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)
