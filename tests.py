import math
import random
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
from typing import Self
import math
import random
import graphviz

do_test_lexer=False
# Testing Lexer
def test_lexer(code):
    lexer = hulk_lexer.lex.lex(module=hulk_lexer)
    lexer.parenthesisCount = 0
    lexer.input(code)

    print("\nCODE")
    print(code)
    while True:
        tok = lexer.token()
        print(tok)
        if not tok: break

if do_test_lexer:
    test_lexer("""type Person(firstname, lastname) {
        firstname = firstname;
        lastname = lastname;

        name() => self.firstname @@ self.lastname;
    }


    type Knight inherits Person {
        name() => "Sir" @@ base();
    }

    let p = new Knight("Phil", "Collins") in
        print(p.name()); // prints 'Sir Phil Collins'
    """)

    test_lexer("""let a = 42, let mod = a % 3 in
        print(
            if (mod == 0) "Magic"
            elif (mod % 3 == 1) "Woke"
            else "Dumb"
        );
    """)

    test_lexer("2+23+3^2**3")

# TESTING CURRENT STATE (experiments)
PI = math.pi
E = math.e

# LLEVAREMOS UN PARENT POR DEFECTO
nodes = {}
def add_slf(slf, nm):
    nodes[slf]=nm

class Node:
    
    id = ""
    parent = None

    def __init__(self):
        add_slf(self,"")


    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass

# class Program(Node):
#     def __init__(self, exp):
#         self.main_exp=exp
#         add_slf(self, 'PROGRAM')

class ExpressionBlock(Node):
    def __init__(self, exps):
        add_slf(self, 'EXP_BLOCK')
        self.exp_list = exps

class Let(Node):
    def __init__(self,assign, body):
        add_slf(self,'LET')
        self.assign = assign
        self.body = body

class Assign(Node):
    def __init__(self, name, value):
        add_slf(self, 'ASSIGN')
        self.name = name
        self.value = value

class ID(Node):
    def __init__(self, name):
        add_slf(self, name)
        self.name=name


# Operations Classes (binary, unary,etc)
class BinOp(Node):
    def __init__(self, left, op, right):
        add_slf(self, str(op))
        self.left = left
        self.op = op
        self.right = right

    def check(
        self,
    ):  # most be modified to works with all binary operators, now only works with '+', '-', '*', '/'
        # Check the operands
        self.left.check()
        self.right.check()

        # Check the operator
        if self.op not in ["+", "-", "*", "/"]:
            raise TypeError(f"Invalid operator: {self.op}")

        # Infer the types of the operands
        left_type = self.left.infer_type()
        right_type = self.right.infer_type()

        # Check that the types are compatible
        if left_type != right_type:
            raise TypeError(f"Type mismatch: {left_type} {self.op} {right_type}")

        # Check that the types are valid for the operation
        if left_type != "number":
            raise TypeError(f"Invalid type for operation: {left_type}")

    def infer_type(self):
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


class UnaryOp(Node):
    def __init__(self, op, operand):
        add_slf(self, str(op))
        self.op = op
        self.operand = operand

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


# number class
class Num(Node):
    def __init__(self, value):
        add_slf(self, str(value))
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value

    def check(self):
        # Check that the value is a number
        if not isinstance(self.value, (float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        # The type of a number is 'num'
        return "number"

    def eval(self):
        return self.value


# constants classes
class Pi(Node):
    def __init__(self):
        add_slf(self,'PI')

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return PI


class E(Node):
    def __init__(self):
        add_slf(self,'E')

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return E


# built-in functions classes
class Print(
    Node
):  # most be modified to work with all literals, now only works with numbers, missing strings and booleans
    def __init__(self, value):
        add_slf(self, "PRINT")
        self.value = value

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def eval(self):
        print(self.value.eval())


class Sqrt(Node):
    def __init__(self, value):
        add_slf(self,"SQRT")
        self.value = value

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


class Sin(Node):
    def __init__(self, value):
        add_slf(self, "SIN")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sin(self.value.eval())


class Cos(Node):
    def __init__(self, value):
        add_slf(self, "COS")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.cos(self.value.eval())


class Exp(Node):
    def __init__(self, value):
        add_slf(self,"EXP")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.exp(self.value.eval())


class Log(Node):
    def __init__(self, value, base):
        add_slf(self,"LOG")
        self.base = base
        self.value = value

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

    def infer_type(self):
        return "number"

    def eval(self):
        return math.log(self.base.eval(), self.value.eval())


class Rand(Node):
    def __init__(self):
        add_slf(self,"RAND")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return random.uniform(0, 1)



lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

# precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "UMINUS"),
)

# dictionary of names (for storing variables)
names = {}

def p_empty(p):
    'empty :'
    pass


def p_program(p):
    "program : hl_expression"
    p[0] = p[1]


def p_hl_expression(p):
    """hl_expression : expression SEMI
					| expression_block
	"""
    p[0] = p[1]

def p_expression_tbl(p):
    """expression : expression_block
	"""
    p[0]=p[1]

def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    p[0] = ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]

def p_expression_block_list(p):
    "expression_block_list : hl_expression expression_block_list"
    p[0]=[]
    p[0].append(p[1])
    p[0]=p[0]+p[2]

def p_expression_block_list_empty(p):
    """expression_block_list : empty
	"""
    p[0]=[]

def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression
	"""
    p[0]=Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]

def p_let(p):
    """expression : LET assign_values IN expression
	"""
    p[0]=Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]

def p_assign_values(p):
    """assign_values : NAME EQUAL expression rem_assignments
	"""
    p[0]=[]
    id = ID(p[1])
    assign = Assign(id, p[3])
    id.parent=assign
    p[3].parent = assign
    p[0].append(assign)
    p[0]=p[0]+p[4]

def p_rem_assignments(p):
    "rem_assignments : COMMA NAME EQUAL expression rem_assignments"

    p[0]=[]
    id = ID(p[2])
    assign = Assign(id, p[4])
    id.parent=assign
    p[4].parent = assign
    p[0].append(assign)
    p[0]=p[0]+p[5]

def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0]=[]

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression"""
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent=p[0]
    p[3].parent=p[0]


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])


# constants
def p_expression_pi(p):
    "expression : PI"
    p[0] = Pi()


def p_expression_e(p):
    "expression : E"
    p[0] = E()


# Built-in functions
def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
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


def p_error(p):
    if p:
        print(f"Syntax error at {p.value}")
    else:
        print("Syntax error at EOF")





# Generate AST
parser = yacc.yacc(start="program")

hulk_code = """let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
                            rand();}
                {print(rand()-5*3+2);
                            rand();} 
                            2*23+123;
                {let x=2 in let a=7 in print(1+5);
                 print(let asd=4 in {rand();}); }
                {{{print(sin((PI*(((1/2)))+PI)));}}}{{{}}} };"""
# hulk_code = "print(PI-E);"

AST = parser.parse(hulk_code)

def create_AST_graph(dict: dict):
    dot = graphviz.Digraph("AST")
    for key in dict.keys():
        if not key.parent:
            dict[key]+=" ( </> )"
        dot.node(str(key), dict[key])
    for key in dict.keys():
        if key.parent:
            dot.edge(str(key.parent), str(key))
    dot.render(directory='output')

create_AST_graph(nodes)
