from .stmt import Block, Expression, Function, If, Print, Return, Var, While
from .expr import Assign, Binary, Call, Grouping, Literal, Logical, Unary, Variable
from .errors import ParseError
from .tokenizer import Tt


class Parser:
    def __init__(self, lox, tokens):
        self.lox = lox
        self.tokens = tokens
        self.current = 0

    def match(self, *types):
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, t, message):
        if self.check(t):
            self.advance()
            return self.prev()
        raise self.error(self.peek(), message)

    def error(self, token, message):
        self.lox.error(token.line, f"Error with token {token}: {message}")
        return ParseError()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.prev().type == Tt.SEMI:
                return
            if self.peek().type in [
                Tt.CLASS,
                Tt.FUN,
                Tt.VAR,
                Tt.FOR,
                Tt.IF,
                Tt.WHILE,
                Tt.PRINT,
                Tt.RETURN,
            ]:
                return
            self.advance()

    def check(self, t):
        if self.is_at_end():
            return False
        return self.peek().type == t

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.prev()

    def is_at_end(self):
        return self.peek().type == Tt.EOF

    def peek(self):
        return self.tokens[self.current]

    def prev(self):
        return self.tokens[self.current - 1]

    def expression(self):
        return self.assignment()

    def declaration(self):
        try:
            if self.match(Tt.FUN):
                return self.fun_declaration("function")
            if self.match(Tt.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def fun_declaration(self, kind):
        name = self.consume(Tt.IDENTIFIER, f"expected {kind} name")
        self.consume(Tt.LEFT_PAREN, "( expected at the beginning of function definition")
        params = []
        if not self.check(Tt.RIGHT_PAREN):
            params.append(self.consume(Tt.IDENTIFIER, "Parameter name expected"))
            while self.match(Tt.COMMA):
                if len(params) >= 255:
                    self.lox.error(self.peek().line, "can't have more than 255 parameters")
                params.append(self.consume(Tt.IDENTIFIER, "Parameter name expected"))

        self.consume(Tt.RIGHT_PAREN, ") expected at the end of parameter list")
        self.consume(Tt.LEFT_BRACE, "{ expected at the beginning of function definition")

        body = self.block()

        return Function(name, params, body)

    def var_declaration(self):
        name = self.consume(Tt.IDENTIFIER, "expect a variable name")
        initializer = None
        if self.match(Tt.EQUAL):
            initializer = self.expression()
        self.consume(Tt.SEMI, "Semi expected after variable declaration")
        return Var(name, initializer)

    def statement(self):
        if self.match(Tt.PRINT):
            return self.print_statement()
        if self.match(Tt.LEFT_BRACE):
            return Block(self.block())
        if self.match(Tt.IF):
            return self.if_statement()
        if self.match(Tt.WHILE):
            return self.while_statement()
        if self.match(Tt.FOR):
            return self.for_statement()
        if self.match(Tt.RETURN):
            return self.return_statement()
        return self.expression_statement()

    def print_statement(self):
        value = self.expression()
        self.consume(Tt.SEMI, "expect semi after statement")
        return Print(value)

    def block(self):
        statements = []
        while not self.check(Tt.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(Tt.RIGHT_BRACE, "Right brace expected after block.")
        return statements

    def if_statement(self):
        self.consume(Tt.LEFT_PAREN, "( expected after if")
        condition = self.expression()
        self.consume(Tt.RIGHT_PAREN, ") expected at the end of if")
        thenbranch = self.statement()
        elsebranch = None
        if self.match(Tt.ELSE):
            elsebranch = self.statement()
        return If(condition, thenbranch, elsebranch)

    def while_statement(self):
        self.consume(Tt.LEFT_PAREN, "( expected at the beginning of while")
        condition = self.expression()
        self.consume(Tt.RIGHT_PAREN, ") expected at the end of while")
        body = self.statement()
        return While(condition, body)

    def for_statement(self):
        self.consume(Tt.LEFT_PAREN, "( expected at the beginning of for")
        initializer = None
        if self.match(Tt.VAR):
            initializer = self.var_declaration()
        elif self.match(Tt.SEMI):
            pass
        else:
            initializer = self.expression_statement()
        condition = None
        if not self.check(Tt.SEMI):
            condition = self.expression()
        self.consume(Tt.SEMI, "; expected after for condition")
        increment = None
        if not self.check(Tt.RIGHT_PAREN):
            increment = self.expression()
        self.match(Tt.RIGHT_PAREN, ") expected at the end of for statement")
        body = self.statement()

        if increment is not None:
            body = Block([body, Expression(increment)])
        if not condition:
            condition = Literal(True)
        body = While(condition, body)
        if initializer is not None:
            body = Block([initializer, body])

        return body

    def return_statement(self):
        keyword = self.prev()
        value = None
        if not self.check(Tt.SEMI):
            value = self.expression()

        self.consume(Tt.SEMI, "; expected after return")

        return Return(keyword, value)

    def expression_statement(self):
        value = self.expression()
        self.consume(Tt.SEMI, "expect semi after statement")
        return Expression(value)

    def assignment(self):
        expr = self.or_op()
        if self.match(Tt.EQUAL):
            equals = self.prev()
            value = self.assignment()
            if type(expr) is Variable:
                name = expr.name
                return Assign(name, value)
            self.lox.error(equals.line, "Invalid assignment target")

        return expr

    def or_op(self):
        expr = self.and_op()
        while self.match(Tt.OR):
            op = self.prev()
            right = self.and_op()
            expr = Logical(expr, op, right)
        return expr

    def and_op(self):
        expr = self.equality()
        while self.match(Tt.AND):
            op = self.prev()
            right = self.equality()
            expr = Logical(expr, op, right)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(Tt.BANG_EQUAL, Tt.EQUAL_EQUAL):
            operator = self.prev()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(Tt.GREATER, Tt.GREATER_EQUAL, Tt.LESS, Tt.LESS_EQUAL):
            operator = self.prev()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()
        while self.match(Tt.MINUS, Tt.PLUS):
            operator = self.prev()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()
        while self.match(Tt.SLASH, Tt.STAR):
            operator = self.prev()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(Tt.BANG, Tt.MINUS):
            operator = self.prev()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self):
        expr = self.primary()

        while True:
            if self.match(Tt.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break

        return expr

    def finish_call(self, callee):
        args = []
        if not self.check(Tt.RIGHT_PAREN):
            if len(args) >= 255:
                self.lox.error(self.peek().line, "can't have more than 255 arguments.")
            args.append(self.expression())
            while self.match(Tt.COMMA):
                args.append(self.expression())

        paren = self.consume(Tt.RIGHT_PAREN, ") expected after argument list")
        return Call(callee, paren, args)

    def primary(self):
        if self.match(Tt.FALSE):
            return Literal(False)
        if self.match(Tt.TRUE):
            return Literal(True)
        if self.match(Tt.NIL):
            return Literal(None)

        if self.match(Tt.NUMBER, Tt.STRING):
            return Literal(self.prev().literal)

        if self.match(Tt.IDENTIFIER):
            return Variable(self.prev())

        if self.match(Tt.LEFT_PAREN):
            expr = self.expression()
            self.consume(Tt.RIGHT_PAREN, "right paren expected after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "expected expression")

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements
