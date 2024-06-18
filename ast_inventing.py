# calclex.py
#
# tokenizer for a simple expression evaluator for
# numbers and +,-,*,/
# ------------------------------------------------------------
import ply
import ply.lex as lex

# List of token names.   This is always required
tokens = (
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
)

# Regular expression rules for simple tokens
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"


# A regular expression rule with some action code
def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer
lexer = lex.lex()

import ply.yacc as yacc

# precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("nonassoc", "UMINUS"),
)

# dictionary of names (for storing variables)
names = {}


def p_statement_expr(p):
    "statement : expression"
    p[0] = p[1]


class Node:

    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass


class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def check(self):
        # Check the operands
        self.left.check()
        self.right.check()

        # Check the operator
        if self.op not in ["+", "-", "*", "/"]:
            raise TypeError(f"Invalid operator: {self.op}")

    def infer_type(self):
        # Infer the types of the operands
        left_type = self.left.infer_type()
        right_type = self.right.infer_type()

        # Check that the types are compatible
        if left_type != right_type:
            raise TypeError(f"Type mismatch: {left_type} {self.op} {right_type}")

        # The type of a binary operation is the type of its operands
        return left_type

    def eval(self):
        if self.op == "+":
            return self.left.eval() + self.right.eval()
        elif self.op == "-":
            return self.left.eval() - self.right.eval()
        elif self.op == "*":
            return self.left.eval() * self.right.eval()
        elif self.op == "/":
            return self.left.eval() / self.right.eval()


class Num(Node):
    def __init__(self, value):
        self.value = value

    def check(self):
        # Check that the value is a number
        if not isinstance(self.value, (int, float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        # The type of a number is 'num'
        return "num"

    def eval(self):
        return self.value


# Modify your parser rules to generate AST nodes
def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression"""
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])


def p_error(p):
    if p:
        print(f"Syntax error at {p.value}")
    else:
        print("Syntax error at EOF")


# Define the UMINUS symbol in your grammar
def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"
    p[0] = -p[2]


# Generate C code from AST
def generate_c_code(node):
    if isinstance(node, BinOp):
        return f"({generate_c_code(node.left)} {node.op} {generate_c_code(node.right)})"
    elif isinstance(node, Num):
        return str(node.value)
    else:
        raise TypeError(f"Unknown node {node}")


# Write C code to file
def write_c_code_to_file(ast, filename):
    c_code = generate_c_code(ast)
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n\n")
        f.write("int main() {\n")
        f.write(f"    int result = {c_code};\n")
        f.write('    printf("%d\\n", result);\n')
        f.write("    return 0;\n")
        f.write("}\n")


parser = yacc.yacc()
# Generate AST
ast = parser.parse("3 + 4 * 2")

# Generate C code
write_c_code_to_file(ast, "output.c")
