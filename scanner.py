from sly import Lexer


class Scanner(Lexer):
    tokens = {DOTADD, DOTSUB, DOTMUL, DOTDIV,           # matrix binary operators
              ADDASSIGN, SUBASSIGN, MULASSIGN, DIVASSIGN,      # assignment operators
              LE, GE, EQ, NEQ,                          # relational operators
              IF, ELSE, FOR, WHILE,                     # keywords
              BREAK, CONTINUE, RETURN,                  # keywords
              EYE, ZEROS, ONES,                         # keywords
              PRINT,                                    # keyword
              ID,                                       # identifiers
              INTNUM,                                   # integers
              FLOATNUM,                                 # floating-point numbers
              STRING}                                   # strings

    literals = {"(", ")", "[", "]", "{", "}",           # brackets
                "=",                                    # assign
                "+", "-", "*", "/",                     # binary operators
                "<", ">",                               # relational operators
                ":",                                    # extent operator
                ",", ";",                               # comma and semicolon
                "'"}                                    # matrix transposition

    # String containing ignored characters between tokens (special name "ignore")
    ignore = " \t"
    ignore_comment = r"\#.*"

    # relational operators
    LE = r"<="          # Less than or equal to
    GE = r">="          # Greater than or equal to
    EQ = r"=="          # Equal
    NEQ = r"!="         # Not equal

    # assignment operators
    ADDASSIGN = r"\+="
    SUBASSIGN = r"-="
    MULASSIGN = r"\*="
    DIVASSIGN = r"/="

    # matrix binary operators
    DOTADD = r"\.\+"
    DOTSUB = r"\.-"
    DOTMUL = r"\.\*"
    DOTDIV = r"\./"

    # binary operators, brackets, extent operator, 
    # matrix transposition, comma and semicolon
    # all assigned in literals

    # identifiers
    ID = r"[a-zA-Z_][a-zA-Z0-9_]*"

    # keywords
    ID['if'] = IF
    ID['else'] = ELSE
    ID['for'] = FOR
    ID['while'] = WHILE
    ID['break'] = BREAK
    ID['continue'] = CONTINUE
    ID['return'] = RETURN
    ID['eye'] = EYE
    ID['zeros'] = ZEROS
    ID['ones'] = ONES
    ID['print'] = PRINT

    # floating-point numbers
    @_(r"(\d+\.\d*|\d*\.\d+)((E|e)-?\d+)?", 
       r"\d+(E|e)-?\d+")
    def FLOATNUM(self, t):
        t.value = float(t.value)
        return t

    # integers
    @_(r"\d+")
    def INTNUM(self, t):
        t.value = int(t.value)
        return t

    # strings
    @_(r'".*?"')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    # Define a rule so we can track line numbers
    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        print("Line %d: Bad character %r in %r" % (self.lineno, t.value[0], t.value))
        self.index += 1

