from collections import deque
import sys
import AST
from scanner import Scanner
from parser import Mparser
from tree_printer import TreePrinter
from type_checker import TypeChecker
from interpreter import Interpreter


if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "samples/example.txt"

    try:
        file = open(filename, "r")
    except IOError:
        print("Cannot open {0} file".format(filename))
        sys.exit(0)

    text = file.read()

    lexer = Scanner()
    parser = Mparser()

    ast: AST.Program = parser.parse(lexer.tokenize(text))

    if ast:
        typeChecker = TypeChecker()   
        typeChecker.visit(ast)
        typeChecker.report_errors()

        if not typeChecker.errors:
            ast.accept(Interpreter(), toplevel=True)

