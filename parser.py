from sly import Parser
import AST
from scanner import Scanner


class Mparser(Parser):
    tokens = Scanner.tokens
    debugfile = 'parser.out'
    had_error = False

    precedence = (
        ("nonassoc", 'IFX'),
        ("nonassoc", 'ELSE'),
        ("nonassoc", '<', '>', 'LE', 'GE', 'EQ', 'NEQ'),
        ("left", '+', '-', 'DOTADD', 'DOTSUB'),
        ("left", '*', '/', 'DOTMUL', 'DOTDIV'),
        ("right", "\'"),
        ("right", 'UMINUS'),
    )

    start = 'program'

    @_('instruction program')
    def program(self, p):
        if self.had_error:
            return None
        p.program.add_instr(p.instruction)
        return p.program

    @_('instruction')
    def program(self, p):
        return AST.Program(p.lineno, [p.instruction])

    @_('assignment', 
       'if_else_instr',
       'print_instr',
       'loop_instr',
       'block',
       'return_instr',
       'BREAK ";"',
       'CONTINUE ";"')
    def instruction(self, p):
        if isinstance(p[0], AST.Node):
            return p[0]
        return AST.SpecialInstr(p.lineno, p[0])

    #
    # ---------- ASSIGNMENT -----------
    #
    @_('ref "="       expr ";"',
       'ref ADDASSIGN expr ";"',
       'ref SUBASSIGN expr ";"',
       'ref MULASSIGN expr ";"',
       'ref DIVASSIGN expr ";"')
    def assignment(self, p):
        return AST.Assignment(p.lineno, p[1], p.ref, p[2])

    @_('ID')
    def ref(self, p):
        return AST.Variable(p.lineno, p.ID)

    @_('ID "[" indices "]"')
    def ref(self, p):
        return AST.Ref(p.lineno, AST.Variable(p.lineno, p.ID), p.indices)

    @_('expr "," indices')
    def indices(self, p):
        return [p.expr, *p.indices]

    @_('expr')
    def indices(self, p):
        return [p.expr]

    #
    # ----------- IF ELSE INSTRUCTION ------------
    #
    @_('IF "(" expr ")" instruction %prec IFX')
    def if_else_instr(self, p):
        return AST.IfElseInstr(p.lineno, p.expr, p.instruction)

    @_('IF "(" expr ")" instruction ELSE instruction')
    def if_else_instr(self, p):
        return AST.IfElseInstr(p.lineno, p.expr, p.instruction0, p.instruction1)

    @_('IF "(" error ")" instruction %prec IFX',
       'IF "(" error ")" instruction ELSE instruction')
    def if_else_instr(self, _):
        return AST.Error(p.lineno, "Syntax error in if statement. Bad expression")

    #
    # ----------- PRINT INSTRUCTION ------------
    #
    @_('PRINT args ";"')
    def print_instr(self, p):
        return AST.PrintInstr(p.lineno, p.args)

    @_('PRINT error ";"')
    def print_instr(self, _):
        return AST.Error(p.lineno, "Syntax error in print statement. Bad expression")

    @_('arg "," args')
    def args(self, p):
        return [p.arg, *p.args]

    @_('arg')
    def args(self, p):
        return [p.arg]

    @_('expr')
    def arg(self, p):
        return p[0]

    #
    # ----------- LOOP INSTRUCTIONS ------------
    #
    @_('WHILE "(" expr ")" instruction')
    def loop_instr(self, p):
        return AST.WhileLoop(p.lineno, p.expr, p.instruction)

    @_('WHILE "(" error ")" instruction')
    def loop_instr(self, p):
        return AST.Error(p.lineno, "Syntax error in while instruction. Bad expression")
    
    @_('FOR ID "=" expr ":" expr instruction')
    def loop_instr(self, p):
        return AST.ForLoop(p.lineno, AST.Variable(p.lineno, p.ID), AST.Range(p.lineno, p.expr0, p.expr1), p.instruction)

    #
    # ------- BLOCK --------
    #
    @_('"{" program "}"')
    def block(self, p):
        return p.program

    #
    # ------- RETURN INSTRUCTION --------
    #
    @_('RETURN expr ";"')
    def return_instr(self, p):
        return AST.ReturnInstr(p.lineno, p.expr)

    @_('RETURN error ";"')
    def return_instr(self, p):
        return AST.Error(p.lineno, "Syntax error in return statement. Bad expression")

    #
    # ----------- EXPRESSION -------------
    #
    @_('expr "+" expr',
       'expr DOTADD expr',
       'expr "-" expr',
       'expr DOTSUB expr',
       'expr "*" expr',
       'expr DOTMUL expr',
       'expr "/" expr',
       'expr DOTDIV expr',
       'expr "<" expr',
       'expr ">" expr',
       'expr LE expr',
       'expr GE expr',
       'expr EQ expr',
       'expr NEQ expr')
    def expr(self, p):
        return AST.BinExpr(p.lineno, p[1], p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('"(" error ")"')
    def expr(self, p):
        return AST.Error(p.lineno, "Syntax error. Bad expression")

    @_('"-" expr %prec UMINUS ')
    def expr(self, p):
        return AST.UnaryExpr(p.lineno, "-", p.expr)

    @_('expr "\'"')
    def expr(self, p):
        return AST.UnaryExpr(p.lineno, "TRANSPOSE", p.expr)

    @_('EYE "(" expr ")"',
       'ZEROS "(" expr ")"',
       'ONES "(" expr ")"')
    def expr(self, p):
        return AST.FunctionCall(p.lineno, p[0], [p.expr])

    @_('ZEROS "(" expr "," expr ")"',
       'ONES "(" expr "," expr ")"')
    def expr(self, p):
        return AST.FunctionCall(p.lineno, p[0], [p.expr0, p.expr1])

    @_('vector')
    def expr(self, p):
        return p[0]

    @_('INTNUM')
    def expr(self, p):
        return AST.IntNum(p.lineno, p[0])

    @_('FLOATNUM')
    def expr(self, p):
        return AST.FloatNum(p.lineno, p[0])

    @_('ref',
       'string')
    def expr(self, p):
        return p[0]

    #
    # ---------- VECTOR INITILIZATION ---------
    #
    @_('"[" innerlist "]"')
    def vector(self, p):
        return AST.Vector(p.lineno, p.innerlist)

    @_('expr "," innerlist')
    def innerlist(self, p):
        return [p.expr, *p.innerlist]

    @_('expr')
    def innerlist(self, p):
        return [p.expr]

    #
    # ---------- STRING ---------
    #
    @_('STRING')
    def string(self, p):
        return AST.String(p.lineno, p.STRING)

    def error(self, p):
        self.had_error = True
        if p:
            print(f"Syntax error at line {p.lineno}: token=({p.type}, '{p.value}')")
        else:
            print("Unexpected end of input")
