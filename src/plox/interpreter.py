from .fun import Fun
from .builtins import Clock
from .env import Env
from .errors import ReturnError, RuntimeError
from .tokenizer import Tt


class Interpreter:
    def __init__(self, lox):
        self.lox = lox
        self.g = Env()
        self.g.define("clock", Clock())
        self.env = self.g

    def is_truthy(self, expr):
        if expr is None:
            return False
        elif type(expr) is bool:
            return expr
        return True

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

    def visit_call(self, expr):
        callee = self.eval(expr.callee)
        args = [self.eval(arg) for arg in expr.arguments]
        if not hasattr(callee, "call"):
            raise RuntimeError(expr.paren, "can only call functions or classes")
        if len(args) != callee.arity():
            raise RuntimeError(expr.paren, f"wrong argument count: expected {callee.arity()}, got {len(args)}")
        return callee.call(self, args)

    def visit_variable(self, expr):
        return self.env.get(expr.name)

    def visit_logical(self, expr):
        left = self.eval(expr.left)
        if expr.operator.type == Tt.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.eval(expr.right)

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
                return left - right
            case Tt.SLASH:
                self.raise_if_not_numbers(op, left, right)
                if right == 0.0:
                    raise RuntimeError(op, "Division by 0")
                return left / right
            case Tt.STAR:
                self.raise_if_not_numbers(op, left, right)
                return left * right
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

    def visit_assign(self, expr):
        value = self.eval(expr.value)
        self.env.assign(expr.name, value)
        return value

    def eval(self, expr):
        return expr.accept(self)

    def eval_block(self, statements, env):
        prev = self.env
        try:
            self.env = env
            for statement in statements:
                self.eval(statement)
        finally:
            self.env = prev

    def visit_print(self, stmt):
        value = self.eval(stmt.expr)
        print(self.stringify(value))

    def visit_block(self, stmt):
        self.eval_block(stmt.statements, Env(self.env))

    def visit_if(self, stmt):
        if self.is_truthy(self.eval(stmt.condition)):
            self.eval(stmt.thenbranch)
        elif stmt.elsebranch is not None:
            self.eval(stmt.elsebranch)

    def visit_while(self, stmt):
        while self.is_truthy(self.eval(stmt.condition)):
            self.eval(stmt.body)

    def visit_return(self, stmt):
        value = None
        if stmt.value:
            value = self.eval(stmt.value)
        raise ReturnError(value)

    def visit_var(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.eval(stmt.initializer)
        self.env.define(stmt.name.lexeme, value)

    def visit_expression(self, stmt):
        self.eval(stmt.expr)

    def visit_function(self, stmt):
        fun = Fun(stmt, self.env)
        self.env.define(stmt.name.lexeme, fun)

    def interpret(self, statements):
        try:
            for statement in statements:
                self.eval(statement)
        except RuntimeError as e:
            self.lox.runtime_error(e)
