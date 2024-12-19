#!/usr/bin/python

from collections import defaultdict
import AST
from symbol_table import SymbolTable, VariableSymbol

ttype = defaultdict(lambda: defaultdict(lambda: defaultdict(str)))

ttype['+']['int']['int'] = 'int'
ttype['+']['int']['float'] = 'float'
ttype['+']['float']['int'] = 'float'
ttype['+']['float']['float'] = 'float'
ttype['+']['str']['str'] = 'str'
ttype['+']['vector']['int'] = 'vector'
ttype['+']['vector']['float'] = 'vector'
ttype['+']['int']['vector'] = 'vector'
ttype['+']['float']['vector'] = 'vector'
ttype['+']['vector']['vector'] = 'vector'

ttype['-']['int']['int'] = 'int'
ttype['-']['int']['float'] = 'float'
ttype['-']['float']['int'] = 'float'
ttype['-']['float']['float'] = 'float'
ttype['-']['vector']['vector'] = 'vector'

ttype['*']['int']['int'] = 'int'
ttype['*']['int']['float'] = 'float'
ttype['*']['float']['int'] = 'float'
ttype['*']['float']['float'] = 'float'
ttype['*']['vector']['vector'] = 'vector'
ttype['*']['str']['int'] = 'str'
ttype['*']['int']['str'] = 'str'

ttype['/']['int']['int'] = 'int'
ttype['/']['int']['float'] = 'float'
ttype['/']['float']['int'] = 'float'
ttype['/']['float']['float'] = 'float'

ttype['>']['int']['int'] = 'bool'
ttype['>']['int']['float'] = 'bool'
ttype['>']['float']['int'] = 'bool'
ttype['>']['float']['float'] = 'bool'

ttype['<']['int']['int'] = 'bool'
ttype['<']['int']['float'] = 'bool'
ttype['<']['float']['int'] = 'bool'
ttype['<']['float']['float'] = 'bool'

ttype['>=']['int']['int'] = 'bool'
ttype['>=']['int']['float'] = 'bool'
ttype['>=']['float']['int'] = 'bool'
ttype['>=']['float']['float'] = 'bool'

ttype['<=']['int']['int'] = 'bool'
ttype['<=']['int']['float'] = 'bool'
ttype['<=']['float']['int'] = 'bool'
ttype['<=']['float']['float'] = 'bool'

ttype['==']['int']['int'] = 'bool'
ttype['==']['int']['float'] = 'bool'
ttype['==']['float']['int'] = 'bool'
ttype['==']['float']['float'] = 'bool'
ttype['==']['vector']['vector'] = 'bool'

ttype['!=']['int']['int'] = 'bool'
ttype['!=']['int']['float'] = 'bool'
ttype['!=']['float']['int'] = 'bool'
ttype['!=']['float']['float'] = 'bool'
ttype['!=']['vector']['vector'] = 'bool'

ttype['.+']['vector']['vector'] = 'vector'
ttype['.-']['vector']['vector'] = 'vector'
ttype['.*']['vector']['vector'] = 'vector'
ttype['./']['vector']['vector'] = 'vector'

ttype['+=']['int']['int'] = 'int'
ttype['+=']['int']['float'] = 'float'
ttype['+=']['float']['int'] = 'float'
ttype['+=']['float']['float'] = 'float'
ttype['+=']['str']['str'] = 'str'
ttype['+=']['vector']['vector'] = 'vector'

ttype['-=']['int']['int'] = 'int'
ttype['-=']['int']['float'] = 'float'
ttype['-=']['float']['int'] = 'float'
ttype['-=']['float']['float'] = 'float'
ttype['-=']['vector']['vector'] = 'vector'

ttype['*=']['int']['int'] = 'int'
ttype['*=']['int']['float'] = 'float'
ttype['*=']['float']['int'] = 'float'
ttype['*=']['float']['float'] = 'float'
ttype['*=']['vector']['vector'] = 'vector'

ttype['/=']['int']['int'] = 'int'
ttype['/=']['int']['float'] = 'float'
ttype['/=']['float']['int'] = 'float'
ttype['/=']['float']['float'] = 'float'


class NodeVisitor(object):

    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)


    def generic_visit(self, node):
        print(f"\n\n There is no {node.__class__.__name__} class in AST.py that inherits node \n\n")
        # raise Error # auxiliary


class TypeChecker(NodeVisitor):

    def __init__(self):
        self.symbol_table = SymbolTable(None, "global")
        self.loop_indent = 0
        self.errors = []


    # ------- EXTRA -------
    def report_errors(self):
        if len(self.errors) > 0:
            print("-- Errors --")
            for error in self.errors:
                print(error)
    # ---------------------
    

    def visit_IntNum(self, node):
        return "int"
    

    def visit_FloatNum(self, node):
        return "float"


    def visit_Variable(self, node):
        symbol = self.symbol_table.get(node.name)
        if symbol is None:
            self.errors.append(f"[line: {node.lineno}] Undeclared variable {node.name}")
            return None
        return symbol.var_type


    def visit_String(self, node):
        return "str"
    

    def visit_Ref(self, node: AST.Ref):
        var_type = self.visit(node.variable)
        if var_type != 'vector':
            self.errors.append(f"[line: {node.lineno}] Cannot access elements of non vector type '{var_type}'")
            return

        symbol = self.symbol_table.get(node.variable.name)
        if symbol is None:
            return

        if len(symbol.dims) < len(node.indices):
            self.errors.append(f"[line: {node.lineno}] Access with wrong dimensions (too many indices)")
            return symbol.elements_type

        for i, index in enumerate(node.indices):
            index_type = self.visit(index)
            if index_type != 'int':
                self.errors.append(f"[line: {node.lineno}] Type error in vector access (indices must be 'int') got '{index_type}'")
            elif isinstance(index, AST.IntNum):
                if index.value < 0 or index.value >= symbol.dims[i]:
                    self.errors.append(f"[line: {node.lineno}] Index out of range: {index.value}")

        return symbol.elements_type


    def visit_Range(self, node):
        start_type = self.visit(node.start)
        end_type = self.visit(node.end)
        if start_type == end_type == "int":
            return "range"
        else:
            self.errors.append(f"[line: {node.lineno}] Type error in range: type of start {start_type}, type of end {end_type}")


# ------- EXPRESSIONS -------


    def visit_BinExpr(self, node: AST.BinExpr):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        op = node.op

        if ttype[op][left_type][right_type] == "":
            self.errors.append(f"[line: {node.lineno}] Type error in binary expression (not supported): {left_type} {op} {right_type}")
            return None

        if left_type == 'vector' and right_type == 'vector':
            left_dims, right_dims = [], []
            if isinstance(node.left, AST.Variable):
                left_dims = self.symbol_table.get(node.left.name).dims
            if isinstance(node.right, AST.Variable):
                right_dims = self.symbol_table.get(node.right.name).dims
            if isinstance(node.left, AST.BinExpr) or isinstance(node.left, AST.FunctionCall) or \
                isinstance(node.left, AST.UnaryExpr) or isinstance(node.left, AST.Vector):
                left_dims = node.left.dims
            if isinstance(node.right, AST.BinExpr) or isinstance(node.right, AST.FunctionCall) or \
                isinstance(node.right, AST.UnaryExpr) or isinstance(node.right, AST.Vector):
                right_dims = node.right.dims

            if (op == '*' and left_dims and right_dims and left_dims[1] != right_dims[0]) \
                or (op != '*' and left_dims and right_dims and left_dims != right_dims):
                    self.errors.append(
                        f"[line: {node.lineno}] Type error in binary expression (wrong dimensions): {left_dims} {op} {right_dims}"
                    )
            
            node.dims = left_dims if left_dims == right_dims else []

        return ttype[op][left_type][right_type]

        
    def visit_UnaryExpr(self, node):
        value_type = self.visit(node.value)
        op = node.op
        if op == "-" and value_type in ["int", "float"]:
            return value_type
        elif op == "TRANSPOSE" and value_type == "vector":
            if isinstance(node.value, AST.Variable):
                node.dims = self.symbol_table.get(node.value.name).dims
            if isinstance(node.value, AST.BinExpr) or isinstance(node.value, AST.FunctionCall) or \
                isinstance(node.value, AST.UnaryExpr) or isinstance(node.value, AST.Vector):
                node.dims = node.value.dims

            return value_type
        else:
            self.errors.append(f"[line: {node.lineno}] Type error in unary expression: {node.op} '{value_type}'")

    
    def visit_Vector(self, node: AST.Vector):
        if not node.values:
            self.errors.append(f"[line: {node.lineno}] Empty vector declaration")
            return "vector"

        height = len(node.values)
        elements_type = None

        if isinstance(node.values[0], AST.Vector):
            width = len(node.values[0].values)

            for value in node.values:
                value_type = self.visit(value)
                if value_type != 'vector':
                    self.errors.append(f"[line: {node.lineno}] x")
                    return "vector"
                elif len(value.values) != width:
                    self.errors.append(f"[line: {node.lineno}] Wrong dimensions in vector declaration")
                    return "vector"

            elements_type = value.elements_type
        else:
            width = height
            height = 1

            for value in node.values:
                value_type = self.visit(value)
                if value_type == 'str':
                    self.errors.append(f"[line: {node.lineno}] String type not allowed in vector")
                    return "vector"
                elif value_type == 'vector':
                    self.errors.append(f"[line: {node.lineno}] x")
                    return "vector"

            elements_type = value_type

        node.dims = [height, width]
        node.elements_type = elements_type

        return "vector"

    
    def visit_FunctionCall(self, node: AST.FunctionCall):
        if node.name in ["eye", "zeros", "ones"]:
            for arg in node.args:
                arg_type = self.visit(arg)
                if arg_type != 'int':
                    self.errors.append(f"[line: {node.lineno}] Wrong argument type in '{node.name}' function call: '{arg_type}' (should be 'int')")

            for arg in node.args:
                if isinstance(arg, AST.IntNum):
                    node.dims.append(arg.value)
                else:
                    node.dims.append(-1)

            if len(node.args) == 1:
                node.dims.append(node.dims[0])

            node.elements_type = 'float'

            return "vector"
        else:
            self.errors.append(f"[line: {node.lineno}] Undefined function: {node.name}")
 

# ---------- INSTRUCTIONS ----------


    def visit_Assignment(self, node: AST.Assignment):
        value_type = self.visit(node.value)

        if node.instr == '=':
            if isinstance(node.ref, AST.Ref):
                if value_type in ['str', 'vector']:
                    self.errors.append(f"[line: {node.lineno}] Cannot assign value of type '{value_type}' to a vector element")
                return self.visit(node.ref)
            elif isinstance(node.ref, AST.Variable):
                var_name = node.ref.name

                if isinstance(node.value, AST.Vector) or isinstance(node.value, AST.FunctionCall):
                    var_symbol = VariableSymbol(var_name, value_type, node.value.dims, node.value.elements_type)
                else:
                    var_symbol = VariableSymbol(var_name, value_type)

                self.symbol_table.put(var_name, var_symbol)

                return value_type

        else:
            if isinstance(node.ref, AST.Ref):
                if value_type in ['str', 'vector']:
                    self.errors.append(f"[line: {node.lineno}] Cannot assign value of type '{value_type}' to a vector element")
                return self.visit(node.ref)
            elif isinstance(node.ref, AST.Variable):
                variable_type = self.visit(node.ref)
                if variable_type is None:
                    return value_type

                value_type = ttype[node.instr][variable_type][value_type]
                var_symbol = VariableSymbol(node.ref.name, value_type)
                self.symbol_table.put(node.ref.name, var_symbol)
                return value_type
    

    def visit_ReturnInstr(self, node):
        return self.visit(node.value)


    def visit_SpecialInstr(self, node: AST.SpecialInstr):
        if (not (self.symbol_table.scope_name in {"for", "while"})):
            self.errors.append(f"[line: {node.lineno}] Usage of '{node.name}' out of loop")


    def visit_IfElseInstr(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != "bool":
            self.errors.append(f"[line: {node.lineno}] Type error in condition in if-else: '{condition_type}'")
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)


    def visit_PrintInstr(self, node):
        for arg in node.args:
            self.visit(arg)


    def visit_ForLoop(self, node: AST.ForLoop):
        range_type = self.visit(node.var_range)
        if range_type != "range":
            self.errors.append(f"[line: {node.lineno}] Type error in range in for loop: {range_type}")

        self.symbol_table = self.symbol_table.pushScope("for")
        self.loop_indent += 1

        self.symbol_table.put(node.variable.name, VariableSymbol(node.variable.name, "int"))
        self.visit(node.block)

        self.symbol_table = self.symbol_table.popScope()
        self.loop_indent -= 1


    def visit_WhileLoop(self, node: AST.WhileLoop):
        condition_type = self.visit(node.condition)
        if condition_type != "bool":
            self.errors.append(f"[line: {node.lineno}] Type error in condition in while-loop '{condition_type}'")

        self.symbol_table = self.symbol_table.pushScope("while")
        self.loop_indent += 1

        self.visit(node.block)

        self.symbol_table = self.symbol_table.popScope()
        self.loop_indent -= 1


# ---------- OTHER ----------


    def visit_Program(self, node: AST.Program):
        for instruction in node.instructions:
            self.visit(instruction)
        

    def visit_Error(self, node):
        if self.visit(node.msg) != "str":
            self.errors.append(f"[line: {node.lineno}] Type error in error message: {self.visit(node.msg)}")
