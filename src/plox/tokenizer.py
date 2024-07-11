from enum import Enum

Tt = Enum(
    "Tt",
    "LEFT_PAREN RIGHT_PAREN LEFT_BRACE RIGHT_BRACE COMMA DOT MINUS PLUS SEMI SLASH STAR BANG BANG_EQUAL EQUAL EQUAL_EQUAL GREATER GREATER_EQUAL LESS LESS_EQUAL IDENTIFIER STRING NUMBER AND CLASS ELSE FALSE FUN FOR IF NIL OR PRINT RETURN SUPER THIS TRUE VAR WHILE EOF",
)


class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type, self.lexeme, self.literal, self.line = (
            type,
            lexeme,
            literal,
            line,
        )

    def __repr__(self):
        return f"{self.type} {self.lexeme} {self.literal}"


class Tokenizer:
    def __init__(self, lox, source):
        self.lox = lox
        self.start, self.current = 0, 0
        self.line = 1
        self.tokens = []
        self.source = source
        self.source_len = len(self.source)

        self.singles = {
            "(": Tt.LEFT_PAREN,
            ")": Tt.RIGHT_PAREN,
            "{": Tt.LEFT_BRACE,
            "}": Tt.RIGHT_BRACE,
            ",": Tt.COMMA,
            ".": Tt.DOT,
            "+": Tt.PLUS,
            "-": Tt.MINUS,
            ";": Tt.SEMI,
            "*": Tt.STAR,
        }

        self.doubles = {
            "!": ("=", Tt.BANG_EQUAL, Tt.BANG),
            "=": ("=", Tt.EQUAL_EQUAL, Tt.EQUAL),
            "<": ("=", Tt.LESS_EQUAL, Tt.LESS),
            ">": ("=", Tt.GREATER_EQUAL, Tt.GREATER),
        }

        self.keywords = {
            "and": Tt.AND,
            "class": Tt.CLASS,
            "else": Tt.ELSE,
            "false": Tt.FALSE,
            "for": Tt.FOR,
            "fun": Tt.FUN,
            "if": Tt.IF,
            "nil": Tt.NIL,
            "or": Tt.OR,
            "print": Tt.PRINT,
            "return": Tt.RETURN,
            "super": Tt.SUPER,
            "this": Tt.THIS,
            "true": Tt.TRUE,
            "var": Tt.VAR,
            "while": Tt.WHILE,
        }

    def is_at_end(self):
        return self.current >= self.source_len

    def advance(self):
        c = self.source[self.current]
        self.current += 1
        return c

    # We intentionally have peek and peek2 because we only want two characters of lookahead
    def peek(self):
        if self.is_at_end():
            return "\0"
        return self.source[self.current]

    def peek2(self):
        if self.current + 1 >= self.source_len:
            return "\0"
        return self.source[self.current + 1]

    def match(self, c):
        if self.is_at_end():
            return False
        if self.peek() != c:
            return False

        self.advance()
        return True

    def one_char(self):
        char = self.advance()
        return Token(self.singles[char], self.source[self.start:self.current], None, self.line)

    def two_chars(self):
        char = self.advance()
        tup = self.doubles[char]
        return Token(tup[1] if self.match(tup[0]) else tup[2], self.source[self.start:self.current], None, self.line)

    def comment(self):
        if self.match("/"):
            while self.peek() != "\n" and not self.is_at_end():
                self.advance()
        else:
            return Token(
                Tt.SLASH,
                self.source[self.start : self.current],
                None,
                self.line,
            )

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.lox.error(self.line, "unterminated string")
            return

        self.advance()  # closing quote
        return Token(
            Tt.STRING,
            # Strip off the quotes
            self.source[self.start + 1 : self.current - 1],
            self.source[self.start + 1 : self.current - 1],
            self.line,
        )

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == "." and self.peek2().isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()

        return Token(
            Tt.NUMBER,
            self.source[self.start : self.current],
            float(self.source[self.start : self.current]),
            self.line,
        )

    def identifier(self):
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        return Token(
            self.keywords.get(
                self.source[self.start : self.current], Tt.IDENTIFIER
            ),
            self.source[self.start : self.current],
            self.source[self.start : self.current],
            self.line,
        )

    def get_next_token(self):
        if self.peek() in self.singles:
            return self.one_char()
        if self.peek() in self.doubles:
            return self.two_chars()
        match self.advance():
            case "/":
                return self.comment()
            case '"':
                return self.string()
            case " " | "\r" | "\t":
                return
            case "\n":
                self.line += 1
            case s:
                if s.isdigit():
                    return self.number()
                elif s.isalpha() or s == "_":
                    return self.identifier()
                else:
                    self.lox.error(self.line, "Invalid lexeme.")

    def tokenize(self):
        while not self.is_at_end():
            self.start = self.current

            t = self.get_next_token()
            if t:
                self.tokens.append(t)

        self.tokens.append(Token(Tt.EOF, "", None, self.line))

        return self.tokens
