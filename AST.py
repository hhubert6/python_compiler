from dataclasses import dataclass


class Node(object):
    def printTree(self, indent=0):
        pass


# --------- TYPES ---------


@dataclass
class IntNum(Node):
    value: int


@dataclass
class FloatNum(Node):
    value: float


@dataclass
class Variable(Node):
    name: str


@dataclass
class String(Node):
    name: str


@dataclass
class Ref(Node):
    variable: Variable
    indexes: list[Node]


@dataclass
class Range(Node):
    start: Node
    end: Node


# ------- EXPRESSIONS -------


@dataclass
class BinExpr(Node):
    op: str
    left: Node
    right: Node


@dataclass
class UnaryExpr(Node):
    op: str
    value: Node


@dataclass
class Vector(Node):
    values: list[Node]


@dataclass
class FunctionCall(Node):
    name: str
    arg: Node


# ---------- INSTRUCTIONS ----------


@dataclass
class Assignment(Node):
    instr: str
    ref: Ref | Variable
    value: BinExpr | String


@dataclass
class ReturnInstr(Node):
    value: Node


@dataclass
class SpecialInstr(Node):
    name: str


@dataclass
class IfElseInstr(Node):
    condition: Node
    then_block: Node
    else_block: Node | None = None


@dataclass
class PrintInstr(Node):
    args: list[Node]


@dataclass
class ForLoop(Node):
    variable: Variable
    var_range: Range
    block: Node


@dataclass
class WhileLoop(Node):
    condition: Node
    block: Node


# ---------- OTHER ----------


class Program(Node):
    def __init__(self, instructions: list[Node]):
        self.instructions = instructions

    def add_instr(self, instr: Node):
        self.instructions.insert(0, instr)


@dataclass
class Error(Node):
    msg: str
