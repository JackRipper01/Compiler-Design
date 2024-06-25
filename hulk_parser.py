import re
from typing import Self
import math
import random

# constants
PI = math.pi
E = math.e

# lexer
import hulk_lexer
from hulk_lexer import tokens

# Build the lexer
lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

###############################################################################################
###############################################################################################

# Node Classes
###################################################################################

import graphviz

# region classes##################################

# LLEVAREMOS UN PARENT POR DEFECTO
nodes = {}


def add_slf(slf, nm):
    nodes[slf] = nm


def create_AST_graph(dict: dict):
    dot = graphviz.Digraph("AST")
    for key in dict.keys():
        if not key.parent:
            dict[key] += " ( </> )"
        dot.node(str(key), dict[key])
    for key in dict.keys():
        if key.parent:
            dot.edge(str(key.parent), str(key))
    dot.render(directory="output")


class Node:
    id = ""
    parent = None

    def __init__(self):
        add_slf(self, "")

    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass

    def build(self):
        pass


# class Program(Node):
#     def __init__(self, exp):
#         self.main_exp=exp
#         add_slf(self, 'PROGRAM')


class ExpressionBlock(Node):
    def __init__(self, exps):
        add_slf(self, "EXP_BLOCK")
        self.exp_list = exps


class Let(Node):
    def __init__(self, assign, body):
        add_slf(self, "LET")
        self.assign = assign
        self.body = body


class Assign(Node):
    def __init__(self, name, value):
        add_slf(self, "ASSIGN")
        self.name = name
        self.value = value


class ID(Node):
    def __init__(self, name):
        add_slf(self, name)
        self.name = name

        self.name=name
        self.opt_type = opt_type

class If(Node):
    def __init__(self, cond_expr):
        add_slf(self, "IF")
        self.cond_expr = cond_expr

class Case(Node):
    def __init__(self, condition, body, branch):
        add_slf(self, "IF "+ branch)
        self.condition = condition
        self.body = body

class TrueLiteral(Node):
    def __init__(self):
        add_slf(self, "TRUE")

class FalseLiteral(Node):
    def __init__(self):
        add_slf(self, "FALSE")

#region JTR AST

# Operations Classes (binary, unary,etc)
class BinOp(Node):

    def __init__(self, left, op, right):
        add_slf(self, str(op))
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

    def check(
        self,
    ):
        # Check the operands
        self.left.check()
        self.right.check()

        # Check the operator
        if self.op not in ["+", "-", "*", "/", "^", "**", "@"]:
            raise TypeError(f"Invalid operator: {self.op}")

        # Infer the types of the operands
        left_type = self.left.infer_type()
        right_type = self.right.infer_type()

        # Check that the types are valid for the operation
        if self.op in ["+", "-", "*", "/"]:
            if left_type != "number" or right_type != "number":
                raise TypeError(f"Invalid type for operation: {left_type}")
        if self.op in ["^", "**"]:
            if (
                left_type != "string"
                and left_type != "number"
                or right_type != "number"
                and right_type != "string"
            ):
                raise TypeError(f"Invalid type for operation: {left_type}")
        if self.op == "@":
            if (
                left_type != "string"
                and left_type != "number"
                or right_type != "string"
                and right_type != "number"
            ):
                raise TypeError(f"Invalid type for operation: {left_type}")

    def infer_type(
        self,
    ):  # posible error en la inferencia de tipos al checkear un solo miembro
        # Infer the types of the operands
        left_type = self.left.infer_type()

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
            right = self.right.eval()
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return self.left.eval() / right
        elif self.op == "^" or self.op == "**":
            if self.left.eval() < 0 and self.right.eval() != int(self.right.eval()):
                raise ValueError("negative number raised to a non-integer power")
            return self.left.eval() ** self.right.eval()
        elif self.op == "@":
            # Evaluate both operands
            left_eval = self.left.eval()
            right_eval = self.right.eval()

            # Convert operands to strings if necessary and concatenate
            return str(left_eval) + str(right_eval)

    def build(self):
        if self.op in ["+", "-", "*", "/"]:
            return f"({self.left.build()} {self.op} {self.right.build()})"
        elif self.op in ["^", "**"]:
            return f"pow({self.left.build()}, {self.right.build()})"
        elif self.op == "@":
            return f"(concatenate_strings({self.left.build()}, {self.right.build()}))"
        else:
            raise TypeError(f"Unknown operator {self.op}")


class UnaryOp(Node):
    def __init__(self, op, operand):
        add_slf(self, str(op))
        self.op = op
        self.operand = operand

    def __str__(self):
        return f"UnaryOp({self.op}, {self.operand})"

    def check(
        self,
    ):  # most be modified to works with all unary operators, now only works with '-' and only "-"
        # Check the operand
        self.operand.check()

        # Check the operator
        if self.op != "-":
            raise TypeError(f"Invalid operator: {self.op}")
        if self.operand.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.operand.infer_type()}")

    def infer_type(self):
        # Infer the type of the operand
        operand_type = self.operand.infer_type()

        # The type of a unary operation is the type of its operand
        return operand_type

    def eval(self):
        if self.op == "-":
            return -self.operand.eval()

    def build(self):
        if self.op == "-":
            return f"(-{self.operand.build()})"
        else:
            raise TypeError(f"Unknown unary operator {self.op}")


# number class
class Num(Node):
    def __init__(self, value):
        add_slf(self, str(value))
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value

    def __str__(self):
        return str(self.value)

    def check(self):
        # Check that the value is a number
        if not isinstance(self.value, (float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        # The type of a number is 'num'
        return "number"

    def eval(self):
        return self.value

    def build(self):
        return str(self.value)


class StringLiteral(Node):
    def __init__(self, value):
        add_slf(self, value)
        # eliminate the ' ' from value
        if value[0] == "'" or value[0] == '"':
            value = value[1:-1]
        self.value = value

    def __str__(self):
        return str(self.value)

    def check(self):
        pass

    def infer_type(self):
        return "string"

    def eval(self):
        return self.value

    def build(self):
        return f'"{self.value}"'


# constants classes
class Pi(Node):

    def __init__(self):
        add_slf(self, "PI")

    def __str__(self):
        return "Pi"

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return PI

    def build(self):
        return "M_PI"


class E(Node):

    def __init__(self):
        add_slf(self, "E")

    def __str__(self):
        return "E"

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return E

    def build(self):
        return "M_E"


# endregion
# region built-in functions classes########################
class Print(
    Node
):  # most be modified to work with all literals, now only works with numbers, missing strings and booleans
    def __init__(self, value):
        add_slf(self, "PRINT")
        self.value = value

    def __str__(self):
        return f"Print({self.value})"

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def eval(self):
        print(self.value.eval())

    def build(self):
        valueType = self.value.infer_type()
        if valueType == "number":
            return f'printf("%f\\n", {self.value.build()});'
        elif valueType == "string":
            return f'printf("%s\\n", {self.value.build()});'
        else:
            raise TypeError(f"Unsupported type for Print: {valueType}")


class Sqrt(Node):
    def __init__(self, value):
        add_slf(self, "SQRT")
        self.value = value

    def __str__(self):
        return f"Sqrt({self.value})"

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")
        if self.value.eval() < 0:
            raise ValueError("sqrt of a negative number")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sqrt(self.value.eval())

    def build(self):
        return f"sqrt({self.value.build()})"


class Sin(Node):
    def __init__(self, value):
        add_slf(self, "SIN")
        self.value = value

    def __str__(self):
        return f"Sin({self.value})"

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sin(self.value.eval())

    def build(self):
        return f"sin({self.value.build()})"


class Cos(Node):
    def __init__(self, value):
        add_slf(self, "COS")
        self.value = value

    def __str__(self):
        return f"Cos({self.value})"

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.cos(self.value.eval())

    def build(self):
        return f"cos({self.value.build()})"


class Exp(Node):
    def __init__(self, value):
        add_slf(self, "EXP")
        self.value = value

    def __str__(self):
        return f"Exp({self.value})"

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.exp(self.value.eval())

    def build(self):
        return f"exp({self.value.build()})"


class Log(Node):
    def __init__(self, value, base):
        add_slf(self, "LOG")
        self.base = base
        self.value = value

    def __str__(self):
        return f"Log({self.base}, {self.value})"

    def check(self):
        self.base.check()
        self.value.check()
        if self.base.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in base of log: {self.base.infer_type()}"
            )
        if self.value.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in argument of log: {self.value.infer_type()}"
            )
        if not (self.base.value > 0 and self.base.value != 1):
            raise ValueError(
                "Logarithm base must be greater than 0 and not equal to 1."
            )
        if self.value.value <= 0:
            raise ValueError("Logarithm argument must be greater than 0.")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.log(self.base.eval(), self.value.eval())

    def build(self):
        # Assuming base is a constant number for simplicity, otherwise, log(x) / log(base) can be used.
        if isinstance(self.base, Num) and self.base.value == math.e:
            return f"log({self.value.build()})"
        else:
            return f"(log({self.value.build()}) / log({self.base.build()}))"


class Rand(Node):

    def __init__(self):
        add_slf(self, "RAND")

    def __str__(self):
        return "Rand"

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return random.uniform(0, 1)

    def build(self):
        # Using rand() from stdlib.h, scaled to 0-1 range
        return f"((float)rand() / (float)RAND_MAX)"


# endregion

# Parser########################################################################################
import ply.yacc as yacc

# precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "POWER"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "UMINUS"),
)


# region Defining the Grammatical##########################
def p_empty(p):
    "empty :"
    pass


def p_program(p):
    "program : hl_expression"
    print("Program")
    p[0] = p[1]


def p_hl_expression(p):
    """hl_expression : expression SEMI
    | expression_block
    """
    print("hl_expression")
    p[0] = p[1]


def p_expression_tbl(p):
    """expression : expression_block"""
    print("expression_tbl")
    p[0] = p[1]


def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    print("Expression Block")
    p[0] = ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]


def p_expression_block_list(p):  # wtfffffffffffffff
    "expression_block_list : hl_expression expression_block_list"
    print("expression_block_list")
    p[0] = []
    p[0].append(p[1])
    p[0] = p[0] + p[2]


def p_expression_block_list_empty(p):
    """expression_block_list : empty"""
    p[0] = []


def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression"""
    print("Let in hl_expression")
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_let(p):
    """expression : LET assign_values IN expression"""
    print("Let in expression")
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_assign_values(p):
    """assign_values : NAME EQUAL expression rem_assignments"""
    print("assign_values")
    p[0] = []
    id = ID(p[1])
    assign = Assign(id, p[3])
    id.parent = assign
    p[3].parent = assign
    p[0].append(assign)
    p[0] = p[0] + p[4]


def p_rem_assignments(p):
    "rem_assignments : COMMA NAME EQUAL expression rem_assignments"
    print("rem_assignments")
    p[0] = []
    id = ID(p[2])
    assign = Assign(id, p[4])
    id.parent = assign
    p[4].parent = assign
    p[0].append(assign)
    p[0] = p[0] + p[5]


def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0] = []


def p_if_hl(p):
    "hl_expression : IF expression expression opt_elifs ELSE hl_expression"
    first = Case(p[2],p[3],"if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last
    
    p[0] = If([first]+p[4]+[last])

    for i in p[0].cond_expr:
        i.parent = p[0]
          
def p_if_exp(p):
    "expression : IF expression expression opt_elifs ELSE expression"
    first = Case(p[2],p[3],"if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6],"else")
    else_cond.parent = last
    p[6].parent = last
    
    p[0] = If([first]+p[4]+[last])
    
    for i in p[0].cond_expr:
        i.parent = p[0]

def p_opt_elifs(p):
    "opt_elifs : ELIF expression expression opt_elifs"
    elif_cond = Case(p[2],p[3],"elif")
    p[2].parent = elif_cond
    p[3].parent = elif_cond
    p[0] = [elif_cond]+p[4]

def p_opt_elifs_e(p):
    "opt_elifs : empty"
    p[0] = []


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression MOD expression
    | expression CONCAT expression
    | expression DCONCAT expression
    | expression AND expression
    | expression OR expression
    | expression EQEQUAL expression
    | expression NOTEQUAL expression
    | expression LESSEQUAL expression
    | expression GREATEREQUAL expression
    | expression LESS expression
    | expression GREATER expression
    """
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = StringLiteral(p[1])


# constants
def p_expression_pi(p):
    "expression : PI"
    p[0] = Pi()


def p_expression_e(p):
    "expression : E"
    p[0] = E()

def p_expression_true(p):
    "expression : TRUE"
    p[0] = TrueLiteral()

def p_expression_false(p):
    "expression : FALSE"
    p[0] = FalseLiteral()

# endregion
# region Built-in functions
def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
    print("Print")
    p[0] = Print(p[3])
    p[3].parent = p[0]


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = Sqrt(p[3])
    p[3].parent = p[0]


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = Sin(p[3])
    p[3].parent = p[0]


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = Cos(p[3])
    p[3].parent = p[0]


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = Exp(p[3])
    p[3].parent = p[0]


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = Log(p[3], p[5])
    p[3].parent = p[0]
    p[5].parent = p[0]


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN"
    p[0] = Rand()


# endregion


def p_error(p):
    if p:
        sErrorList.append(f"Syntax error at {p.value} near line: {p.lineno}")
    else:
        print("Syntax error at EOF")




# region mauricio parser llamacion
# parser = yacc.yacc(start="program")

# hulk_code = """let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
#                             rand();}
#                 {print(rand()-5*3+2);
#                             rand();}
#                             2*23+123;
#                 {let x=2 in let a=7 in print(1+5);
#                  print(let asd=4 in {rand();}); }
#                 {{{print(sin((PI*(((1/2)))+PI)));}}}{{{}}} };"""
# # hulk_code = "print(PI-E);"

# AST = parser.parse(hulk_code)
# endregion

parser = yacc.yacc(start="program")

# Generate AST

ex_code = r"""
                   function asd (a,x) {
                    print(a+x);
                   }
                   function asd (a,x) => {
                    print(a+x);
                   }
                   function asd (a,x) => {
                    print(a+x);
                   };
                   function asdf (a,x) => print(-a+x);
                   let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
                            rand();}
                {print(rand()-5*3+2);
                            rand();} 
                            2*23+123;
                {let x=2 in let a:int=7 in print(1+5);
                 print(let asd=4 in {rand();}); AAAAAAA();}
                {{{print(sin((PI*(((1/2)))+PI * x + f() - asd(x,y) )));}}}{{{}}} print('asd'@ "PRINT aaaa \"  "); };"""

AST = parser.parse(
r"""function a(b,c) => print(b+c);
function siuuu: number (x,y,z) {print(x);print(y);print(z);}
{
    let a = 1 in let b: number = a+3 in print (siuuu(-a+b,a,a(b,a)));
    print("asdasd");
    if (a>2) x elif (a<1) z elif (a<1) {z+4;} elif (a<1) z else y;
}
"""
)

# create_AST_graph(nodes)


# region Generate C code from AST########################################################
# def generate_c_code(node):
#     if isinstance(node, BinOp) and node.op in ["+", "-", "*", "/"]:
#         return f"({generate_c_code(node.left)} {node.op} {generate_c_code(node.right)})"
#     elif isinstance(node, BinOp) and node.op in ["^", "**"]:
#         return f"pow({generate_c_code(node.left)}, {generate_c_code(node.right)})"
#     elif isinstance(node, BinOp) and node.op == "@":
#         # Handle the '@' operation for concatenation
#         left_code = generate_c_code(node.left)
#         right_code = generate_c_code(node.right)
#         # Assuming all operands are converted to strings
#         return f"(concatenate_strings({left_code}, {right_code}))"
#     elif isinstance(node, Num):
#         return str(node.value)
#     elif isinstance(node, StringLiteral):
#         return f'"{node.value}"'
#     elif isinstance(node, UnaryOp):
#         return f"{node.op}{generate_c_code(node.operand)}"
#     elif isinstance(node, Print):
#         return f'printf("%f\\n", {generate_c_code(node.value)})'
#     elif isinstance(node, Pi):
#         return "M_PI"
#     elif isinstance(node, E):
#         return "M_E"
#     elif isinstance(node, Sqrt):
#         return f"sqrt({generate_c_code(node.value)})"
#     elif isinstance(node, Sin):
#         return f"sin({generate_c_code(node.value)})"
#     elif isinstance(node, Cos):
#         return f"cos({generate_c_code(node.value)})"
#     elif isinstance(node, Exp):
#         return f"exp({generate_c_code(node.value)})"
#     elif isinstance(node, Log):
#         return f"(log({generate_c_code(node.base)}) / log({generate_c_code(node.value)}))"  # logaritmo se hace asi pq C no admite log de a en base b
#     elif isinstance(node, Rand):
#         return "((float) rand() / (RAND_MAX))"
#     else:
#         raise TypeError(f"Unknown node {node}")
# endregion
# region Generate C code from ast
def generate_c_code(node):
    return node.build()


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    c_code = generate_c_code(ast)
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <math.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("#include <string.h>\n\n")
        f.write(
            """char* concatenate_strings(const char* str1, const char* str2) {
    // Calculate the length needed for the concatenated string
    int length = strlen(str1) + strlen(str2) + 1; // +1 for the null terminator

    // Allocate memory for the concatenated string
    char* result = (char*)malloc(length * sizeof(char));
    if (result == NULL) {
        printf("Memory allocation failed");
        exit(1); // Exit if memory allocation fails
    }

    // Copy the first string and concatenate the second string
    strcpy(result, str1);
    strcat(result, str2);

    return result;
}\n\n"""
        )
        f.write("int main() {\n")
        f.write(f"    {c_code};\n")
        f.write("    return 0;\n")
        f.write("}\n")


# endregion

# Generate C code
# write_c_code_to_file(ast, "out.c")
