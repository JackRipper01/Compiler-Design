from ast import arg

from numpy import isin
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
import random
import math
import graphviz

sErrorList = []
# constants
PI = math.pi
E = math.e


# Build the lexer
lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

# region classes##################################

# LLEVAREMOS UN PARENT POR DEFECTO
nodes = {}


def add_slf(slf, nm):
    nodes[slf] = nm


def create_AST_graph(dict: dict, graph_name):
    dot = graphviz.Digraph(graph_name)
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


class Program(Node):
    function_names = set()  # Class variable to keep track of function names

    def __init__(self, functions, global_expression):
        add_slf(self, "")
        self.functions = functions
        self.global_exp = global_expression

    def build(self):
        if self.functions:
            functions_code = ""
            for function in self.functions:
                functions_code += function.build()
            return functions_code + self.global_exp.build()
        else:
            return self.global_exp.build()

    @classmethod
    def add_function_name(cls, name):
        if name in cls.function_names:
            raise ValueError(f"Function {name} is already defined.")
        cls.function_names.add(name)

    @classmethod
    def function_name_exists(cls, name):
        return name in cls.function_names


class FunctionList(Node):
    def __init__(self, functions_list):
        add_slf(self, "FUNCTIONS")
        self.function_list = functions_list


class FunctionDef(Node):
    def __init__(self, func_id, params, body):
        add_slf(self, "FUNC_DEF")
        self.func_id = func_id
        self.params = params
        self.body = body
        # Check if the function name already exists
        if Program.function_name_exists(self.func_id):
            raise ValueError(f"Function {self.func_id} is already defined.")
        Program.add_function_name(self.func_id)  # Add the function name to the tracker


class FunctionCall(Node):
    def __init__(self, func_id, params):
        add_slf(self, "FUNC_CALL")
        self.func_id = func_id
        self.params = params


class Params(Node):
    def __init__(self, param_list):
        add_slf(self, "params")
        self.param_list = param_list


class ExpressionBlock(Node):
    instance_count = 0  # Class variable to keep track of the number of instances

    def __init__(self, exps):
        ExpressionBlock.instance_count += (
            1  # Increment the counter for each new instance
        )
        self.instance_id = ExpressionBlock.instance_count
        self.name = f"expression_block_{self.instance_id}"
        while Program.function_name_exists(self.name):
            ExpressionBlock.instance_count += 1
            self.instance_id = ExpressionBlock.instance_count
            self.name = f"expression_block_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        add_slf(self, "EXP_BLOCK")
        self.exp_list = exps

    def build(self):
        code = f"float {self.name}() {{\n"

        for i, exp in enumerate(self.exp_list):
            # Check if it's the last expression in the block
            if i == len(self.exp_list) - 1:
                break
            else:
                code += exp.build() +";"+ "\n"

        # el codigo para q la ultima expression retorne es:
        code += self.exp_list[-1].build()
        last_newline_index = code.rfind("\n")

        if last_newline_index != -1:
            substring_after_last_newline = code[last_newline_index + 1 :].lstrip()
            # print(substring_after_last_newline)
            code = (
                code[: last_newline_index + 1]
                + "return "
                + substring_after_last_newline +";"
            )
        else:
            code_without_initial_whitespace = code.lstrip()
            code = "return " + code_without_initial_whitespace+";"
        code += "\n}\n"
        return code


class Let(Node):
    instance_count = 0  # Class variable to keep track of the number of instances

    def __init__(self, assign, body):
        Let.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = (
            Let.instance_count
        )  # Assign the current count to this instance
        # Construct the function name
        self.name = f"let_{self.instance_id}"
        # Check if the function name already exists
        while Program.function_name_exists(self.name):
            Let.instance_count += 1
            self.instance_id = Let.instance_count
            self.name = f"let_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        add_slf(self, "LET")
        self.assign = assign
        self.body = body

    def check(self):
        pass

    def infer_type(self):
        pass

    def build(self):  # generate c code
        return_type = "float"
        # Use instance_id to create a unique function name
        c_code = f"{return_type} let_{self.instance_id}("
        if len(self.assign) == 1:
            c_code += f"float {self.assign[0].name.name}"
        else:
            for assignment in self.assign:
                c_code += f"float {assignment.name.name}, "
            c_code = c_code[:-2]
        c_code += ") {\n"

        # body
        body_code = self.body.build()
        # Sol (working)
        if isinstance(self.body, ExpressionBlock):
            c_code += body_code
            c_code += "return " + self.body.name + "();"
            c_code += "\n}\n"
        else:
            c_code+= body_code
            last_newline_index = c_code.rfind("\n")
            if last_newline_index != -1:
                c_code = (
                    c_code[: last_newline_index + 1]
                    + " return "
                    + c_code[last_newline_index + 1 :]
                    + ";"
                )
                c_code += "\n}\n"
            else:
                raise ValueError(f"Te falto un salto de linea luego de algun {{ o de algun }} antes de llamar a la funcion")

        # arguments of the call
        c_code += f"let_{self.instance_id}("
        if len(self.assign) == 1:
            c_code += f"{self.assign[0].value}"
        else:
            for assignment in self.assign:
                c_code += f"{assignment.value}, "
            c_code = c_code[:-2]
        c_code += ")" + ("" if isinstance(self.parent,Let) else ";")
        return c_code


class Assign(Node):  # example: name = var a ,value = 4
    def __init__(self, name, value):
        add_slf(self, "ASSIGN")
        self.name = name
        self.value = value

    def check(self):
        pass


class ID(Node):
    def __init__(self, name, opt_type):
        if opt_type == "":
            add_slf(self, "var " + name)
        else:
            add_slf(self, opt_type + " " + name)
        self.name = name
        self.opt_type = opt_type

    def infer_type(self):
        return self.opt_type

    def build(self):
        return self.name


class If(Node):
    def __init__(self, cond_expr):
        add_slf(self, "IF")
        self.cond_expr = cond_expr


class Case(Node):
    def __init__(self, condition, body, branch):
        add_slf(self, "IF " + branch)
        self.condition = condition
        self.body = body


class TrueLiteral(Node):
    def __init__(self):
        add_slf(self, "TRUE")


class FalseLiteral(Node):
    def __init__(self):
        add_slf(self, "FALSE")


# region JTR AST


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
            if left_type != "number" or right_type != "number":
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
            return f"(pow({self.left.build()}, {self.right.build()}))"
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
    instance_count = 0  # Class variable to keep track of the number of instances

    def __init__(self, value):
        Print.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Print.instance_count
        # Construct the function name
        func_name = f"print_{self.instance_id}"
        # Check if the function name already exists
        if Program.function_name_exists(func_name):
            raise ValueError(f"Function {func_name} is already defined.")
        Program.add_function_name(func_name)  # Add the function name to the tracker
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
        if self.value.infer_type() == "string":
            code = f"""char* print_{self.instance_id}(char* printable) {{
printf("%s\\n", printable);
return printeable;
}}\nprint_{self.instance_id}({self.value.build()})"""
            return code

        elif self.value.infer_type() == "number":
            code = f"""float print_{self.instance_id}(float printeable) {{
printf("%f\\n", printeable);
return printeable;
}}\nprint_{self.instance_id}({self.value.build()})"""
            return code
        else:
            code = f"""float print_{self.instance_id}(float printeable) {{
printf("%f\\n", printeable);
return printeable;
}}\nprint_{self.instance_id}({self.value.build()})"""
            return code


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
    # ("right", "PRINT","SQRT","SIN","COS","EXP","LOG","RAND"),
    ("nonassoc", "NAME"),
    ("right", "IN", "LET"),
    ("right", "IF", "ELIF", "ELSE"),
    ("nonassoc", "EQUAL"),
    ("left", "COMMA"),
    ("nonassoc", "INLINE"),
    ("left", "CONCAT", "DCONCAT"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQEQUAL", "NOTEQUAL"),
    ("left", "LESSEQUAL", "GREATEREQUAL", "LESS", "GREATER"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("nonassoc", "NOT"),
    ("right", "POWER"),
    ("right", "LPAREN", "LPAREN"),
    ("nonassoc", "UMINUS"),
)


# region Defining the Grammatical##########################
def p_empty(p):
    "empty :"
    pass


def p_opt_type(p):
    "opt_type : COLON NAME"
    p[0] = p[2]


def p_opt_type_e(p):
    "opt_type : empty"
    p[0] = ""


def p_namedef(p):
    "namedef : NAME opt_type"
    p[0] = ID(p[1], p[2])


def p_program(p):
    "program : functions hl_expression"
    p[0] = Program(p[1], p[2])
    p[2].parent = p[0]
    for i in p[1]:
        i.parent = p[0]


# region function grammatical
def p_function_list_items(p):
    "functions : function_def functions"
    p[0] = [p[1]] + p[2]


def p_function_list_items_empty(p):
    "functions : empty"
    p[0] = []


def p_exp_func_call(p):
    "expression : func_call"
    p[0] = p[1]


def p_func_call(p):
    "func_call : NAME LPAREN cs_exps RPAREN"
    id = ID(p[1], "")
    p[0] = FunctionCall(id, p[3])
    id.parent = p[0]
    p[3].parent = p[0]


def p_cs_exps(p):
    "cs_exps : cs_exps_list"
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]


def p_cs_exps_list(p):
    "cs_exps_list : expression cs_exps_list_rem"
    p[0] = [p[1]] + p[2]


def p_cs_exps_list_e(p):
    "cs_exps_list : empty"
    p[0] = []


def p_cs_exps_list_rem(p):
    "cs_exps_list_rem : COMMA expression cs_exps_list_rem"
    p[0] = [p[2]] + p[3]


def p_cs_exps_list_rem_e(p):
    "cs_exps_list_rem : empty"
    p[0] = []


def p_function_def(p):
    "function_def : FUNCTION namedef LPAREN func_params RPAREN INLINE hl_expression"
    p[0] = FunctionDef(p[2], p[4], p[7])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[7].parent = p[0]


def p_function_def_fullform(p):
    "function_def : FUNCTION namedef LPAREN func_params RPAREN expression_block"
    p[0] = FunctionDef(p[2], p[4], p[6])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[6].parent = p[0]


def p_func_params(p):
    "func_params : func_params_list"
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]


def p_func_params_list(p):
    "func_params_list : namedef func_params_list_rem"
    p[0] = [p[1]] + p[2]


def p_func_params_list_e(p):
    "func_params_list : empty"
    p[0] = []


def p_func_params_list_rem(p):
    "func_params_list_rem : COMMA namedef func_params_list_rem"
    p[0] = [p[2]] + p[3]


def p_func_params_list_rem_e(p):
    "func_params_list_rem : empty"
    p[0] = []


# endregion


def p_hl_expression(p):
    """hl_expression : expression SEMI
    | expression_block
    """
    p[0] = p[1]


def p_expression_tbl(p):
    """expression : expression_block"""
    p[0] = p[1]


def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    p[0] = ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]


def p_expression_block_list(p):
    "expression_block_list : hl_expression expression_block_list"
    p[0] = [p[1]] + p[2]


def p_expression_block_list_e(p):
    "expression_block_list : empty"
    p[0] = []


# def p_expression_block_hl(p):
#     "expression_block_hl : LBRACE expression_block_hl_list RBRACE"
#     p[0] = ExpressionBlock(p[2])
#     for i in p[2]:
#         i.parent = p[0]


# def p_expression_block_hl_list(p):
#     "expression_block_hl_list : hl_expression expression_block_hl_list"
#     p[0]=[p[1]]+p[2]

# def p_expression_block_list_e(p):
#     "expression_block_list : empty"
#     p[0] = []


def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression"""
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_let(p):
    """expression : LET assign_values IN expression"""
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_assign_values(p):
    """assign_values : namedef EQUAL expression rem_assignments"""
    assign = Assign(p[1], p[3])
    p[1].parent = assign
    p[3].parent = assign
    p[0] = [assign] + p[4]


def p_rem_assignments(p):
    "rem_assignments : COMMA namedef EQUAL expression rem_assignments"

    assign = Assign(p[2], p[4])
    p[2].parent = assign
    p[4].parent = assign
    p[0] = [assign] + p[5]


def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0] = []


# region if grammatical
def p_if_hl(p):
    "hl_expression : IF expression expression opt_elifs ELSE hl_expression"
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].cond_expr:
        i.parent = p[0]


def p_if_exp(p):
    "expression : IF expression expression opt_elifs ELSE expression"
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].cond_expr:
        i.parent = p[0]


def p_opt_elifs(p):
    "opt_elifs : ELIF expression expression opt_elifs"
    elif_cond = Case(p[2], p[3], "elif")
    p[2].parent = elif_cond
    p[3].parent = elif_cond
    p[0] = [elif_cond] + p[4]


def p_opt_elifs_e(p):
    "opt_elifs : empty"
    p[0] = []


# endregion


def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


# region operations
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


def p_expression_binop_hl(p):
    """hl_expression : expression PLUS hl_expression
    | expression MINUS hl_expression
    | expression TIMES hl_expression
    | expression DIVIDE hl_expression
    | expression POWER hl_expression
    | expression MOD hl_expression
    | expression CONCAT hl_expression
    | expression DCONCAT hl_expression
    | expression AND hl_expression
    | expression OR hl_expression
    | expression EQEQUAL hl_expression
    | expression NOTEQUAL hl_expression
    | expression LESSEQUAL hl_expression
    | expression GREATEREQUAL hl_expression
    | expression LESS hl_expression
    | expression GREATER hl_expression
    """
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_unary(p):
    """expression : MINUS expression %prec UMINUS
    | NOT expression
    """
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_unary_hl(p):
    """hl_expression : MINUS hl_expression %prec UMINUS
    | NOT hl_expression
    """
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = StringLiteral(p[1])


def p_expression_variable(p):
    "expression : NAME"
    p[0] = ID(p[1], "")


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


# region built-in funct grammatical
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


# endregion


def p_error(p):
    sErrorList.append(p)
    # print(sErrorList[-1])


# endregion

# endregion

# region Generate AST

parser = yacc.yacc(start="program", method="LALR")


def find_column(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1

    return (token.lexpos - line_start) + 1


def hulk_parse(code):

    AST = parser.parse(code)

    if len(sErrorList) == 0:
        create_AST_graph(nodes, "AST")
        write_c_code_to_file(AST, "out.c")
    else:
        print("\nPARSING FINISHED WITH ERRORS:")
        for i in sErrorList:
            if i:
                print(
                    " - ",
                    f"Syntax error near '{i.value}' at line {i.lineno}, column {find_column(code,i)}",
                )
            else:
                print("Syntax error at EOF")


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <math.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("#include <string.h>\n\n")
        f.write(
            """//Concatenate two strings
    char* concatenate_strings(const char* str1, const char* str2) {
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
        f.write("int main() {\n\n")
        f.write(f"{ast.build()}\n\n")
        f.write("return 0;\n")
        f.write("}\n")


my_ex_code = """function asd (a,x) {
    print(a+x);
    }{ }"""

my_ex_code2 = (
    f"""let a=5 in let b = 4 in let c=3 in {{a+4;\nprint(a);}}"""
)
print(my_ex_code2)
hulk_parse(my_ex_code2)


# endregion

# Generate C code
