class Resolver:
    def __init__(self, lox, interpreter):
        self.lox = lox
        self.interpreter = interpreter
        self.scopes = []
        self.current_function = None
        self.current_class = None

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if scope.get(name.lexeme):
            self.lox.error(name.line, "already a variable with this name in this scope")
        scope[name.lexeme] = False

    def define(self, name):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr, name):
        for idx, scope in enumerate(self.scopes[::-1]):
            if scope.get(name.lexeme):
                self.interpreter.resolve(expr, idx)

    def visit_block(self, stmt):
        self.begin_scope()
        self.resolve_statements(stmt.statements)
        self.end_scope()

    def visit_class(self, stmt):
        enclosing = self.current_class
        self.current_class = "class"
        self.declare(stmt.name)
        self.define(stmt.name)
        self.begin_scope()
        self.scopes[-1]["this"] = True
        for method in stmt.methods:
            declaration = "method"
            if method.name.lexeme == "init":
                declaration = "initializer"
            self.resolve_function(method, declaration)
        self.end_scope()
        self.current_class = enclosing

    def visit_var(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_variable(self, expr):
        if self.scopes and not self.scopes[-1].get(expr.name.lexeme, True):
            self.lox.error(expr.name.line, "can't read variable in its own initializer")

        self.resolve_local(expr, expr.name)

    def visit_assign(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name)

    def visit_function(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, "function")

    def resolve_statements(self, statements):
        for statement in statements:
            self.resolve(statement)

    def resolve_function(self, function, functype):
        enclosing = self.current_function
        self.current_function = functype
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve_statements(function.body)
        self.end_scope()
        self.current_function = enclosing

    def visit_expression(self, stmt):
        self.resolve(stmt.expr)

    def visit_if(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.thenbranch)
        if stmt.elsebranch:
            self.resolve(stmt.elsebranch)

    def visit_print(self, stmt):
        self.resolve(stmt.expr)

    def visit_return(self, stmt):
        if not self.current_function:
            self.lox.error(stmt.keyword, "can't return from top-level code")
        if stmt.value is not None:
            if self.current_function == "initializer":
                self.lox.error(stmt.keyword, "can't return from initializer")
            self.resolve(stmt.value)

    def visit_while(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_binary(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_logical(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call(self, expr):
        self.resolve(expr.callee)
        for arg in expr.arguments:
            self.resolve(arg)

    def visit_get(self, expr):
        self.resolve(expr.object)

    def visit_set(self, expr):
        self.resolve(expr.value)
        self.resolve(expr.object)

    def visit_this(self, expr):
        if not self.current_class:
            return self.lox.error(expr.keyword.line, "Can't use 'this' outside class")
        self.resolve_local(expr, expr.keyword)

    def visit_grouping(self, expr):
        self.resolve(expr.expression)

    def visit_literal(self, expr):
        pass

        def visit_unary(self, expr):
            self.resolve(expr.right)

    def resolve(self, host):
        host.accept(self)
