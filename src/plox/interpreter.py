from .tokenizer import Tt


class RuntimeError(Exception):
    def __init__(self, token, msg):
        super().__init__(msg)
        self.token = token


class Interpreter:
    def __init__(self, lox):
        self.lox = lox

    def is_truthy(self, expr):
        if expr is None:
            return False
        elif type(expr) is bool:
            return expr
        return False

    def is_equal(self, a, b):
        return a == b

    def raise_if_not_numbers(self, op, a, b):
        if type(a) is float and type(b) is float:
            return
        raise RuntimeError(
            op, f"operands must be numbers, are {a.literal} and {b.literal}"
        )

    def stringify(self, value):
        if value is None:
            return None
        # Quick hack to check if x==x.0
        elif type(value) is float and float(value) == float(int(value)):
            return f"{int(value)}"
        else:
            return str(value)

    def visit_literal(self, expr):
        return expr.value

    def visit_grouping(self, expr):
        return self.eval(expr.expression)

    def visit_unary(self, expr):
        right = self.eval(expr.right)
        if expr.operator.type == Tt.MINUS:
            if type(right) is not float:
                raise RuntimeError(
                    self.right, f"Operand must be an umber, is {right.literal}"
                )
            return -float(right)
        elif expr.operator.type == Tt.BANG:
            return not self.is_truthy(right)

    def visit_binary(self, expr):
        left = self.eval(expr.left)
        op = expr.operator
        right = self.eval(expr.right)

        match op.type:
            case Tt.PLUS:
                if type(left) is float and type(right) is float:
                    return left + right
                elif type(left) is str and type(right) is str:
                    return left + right
                else:
                    raise RuntimeError(
                        op,
                        f"can only add numbers or strings, adding {left.literal} and {right.literal}",
                    )
            case Tt.MINUS:
                self.raise_if_not_numbers(op, left, right)
                return left-right
            case Tt.SLASH:
                self.raise_if_not_numbers(op, left, right)
                if right == 0.0:
                    raise RuntimeError(op, "Division by 0")
                return left/right
            case Tt.STAR:
                self.raise_if_not_numbers(op, left, right)
                return left*right
            case Tt.GREATER:
                self.raise_if_not_numbers(op, left, right)
                return left > right
            case Tt.GREATER_EQUAL:
                self.raise_if_not_numbers(op, left, right)
                return left >= right
            case Tt.LESS:
                self.raise_if_not_numbers(op, left, right)
                return left < right
            case Tt.LESS_EQUAL:
                self.raise_if_not_numbers(op, left, right)
                return left <= right
            case Tt.BANG_EQUAL:
                return not self.is_equal(left, right)
            case Tt.EQUAL_EQUAL:
                return self.is_equal(left, right)

    def eval(self, expr):
        return expr.accept(self)

    def interpret(self, expr):
        try:
            val = self.eval(expr)
            print(self.stringify(val))
        except RuntimeError as e:
            self.lox.runtime_error(e)
