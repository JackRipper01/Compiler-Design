from ast import arg
from calendar import c
from turtle import right

from numpy import isin
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
import random
import math
import graphviz
import io

sErrorList = []

lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

# region AST classes

# LLEVAREMOS UN PARENT POR DEFECTO
# region AST

nodes = {}


def add_slf(slf, nm):
    nodes[slf] = nm


def create_AST_graph(dict: dict, graph_name):
    dot = graphviz.Digraph(graph_name)
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
    def __init__(self, slf, nm):
        nodes[slf] = nm
        self.parent = None
        self.static_type = "Object"
        self.dynamic_type = "Object"
        self.ret_point = "ret_point"

    def check(self):
        pass

    def infer_type(self):
        pass

    def build(self):
        pass


class Program(Node):
    function_names = set()  # Class variable to keep track of function names
    instance_count = 0

    def __init__(self, functions_types, global_expression):
        super().__init__(self, "")
        self.functions = filter(lambda x: type(x) is FunctionDef, functions_types)
        self.types = filter(lambda x: type(x) is TypeDef, functions_types)
        self.global_exp = global_expression

    def build(self):
        code_main = self.global_exp.build()
        with open("./out.c", "w") as f:
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
            if self.functions:
                for function in self.functions:
                    f.write(f"{function.build()[0]}\n\n")
            f.write("float main() {\n\n")
            f.write(f"{code_main[0]}\n\n")
            f.write(f"return {code_main[1]};\n")
            f.write("}\n")

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
        super().__init__(self, "FUNCTIONS")
        self.function_list = functions_list


class FunctionDef(Node):
    def __init__(self, func_id, params, body):
        super().__init__(self, "FUNC_DEF")
        self.func_id = func_id
        self.params = params
        self.body = body
        # Check if the function name already exists
        if Program.function_name_exists(self.func_id):
            raise ValueError(f"Function {self.func_id} is already defined.")
        Program.add_function_name(self.func_id)  # Add the function name to the tracker

    def build(self):
        self.static_type = "float"
        list_params = []
        body_def, body_ret = self.body.build()
        for param in self.params.param_list:
            list_params.append(("float", param.name))
        params_c_code = ""
        for param_code in list_params:
            params_c_code += f"{param_code[0]} {param_code[1]},"
        params_c_code = params_c_code[:-1]
        code = f"""{self.static_type} {self.func_id.name}({params_c_code}){{{body_def}
        return {body_ret};
        }}"""

        return code, ""


class FunctionCall(Node):
    def __init__(self, func_id, params):
        super().__init__(self, "FUNC_CALL")
        self.func_id = func_id
        self.params = params

    def build(self):
        def_ret_list_params = []
        for param in self.params.param_list:
            build_of_param = param.build()
            def_ret_list_params.append(build_of_param)

        params_def_code = ""
        for param_def_code in def_ret_list_params:
            if param_def_code[0] != "":
                params_def_code += param_def_code[0] + "\n"

        params_ret_c_code = ""
        for param_ret_code in def_ret_list_params:
            params_ret_c_code += param_ret_code[1] + ","

        params_ret_c_code = params_ret_c_code[:-1]
        return f"{params_def_code}", f"""{self.func_id.name}({params_ret_c_code})"""


class Params(Node):
    def __init__(self, param_list):
        super().__init__(self, "params")
        self.param_list = param_list


class ExpressionBlock(Node):
    def __init__(self, exps):
        super().__init__(self, "EXP_BLOCK")
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"expression_block_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"expression_block_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        self.exp_list = exps

    def build(self):
        self.static_type = "float"
        self.ret_point = "ret_point_expression_block_" + str(
            self.instance_id
        )  # analizar lo del id pa q no haya lio
        code = f"""{self.static_type} {self.name}() {{
        """
        for exp, i in zip(self.exp_list, range(len(self.exp_list))):
            body_def, body_ret = exp.build()
            code += body_def + "\n"
            if i == len(self.exp_list) - 1:
                code += f"return {body_ret};\n"
        code += "}"
        code += f"""{self.static_type} {self.ret_point} = expression_block_{self.instance_id}();"""
        return code, self.ret_point

        # region old
        # code = f"float {self.name}() {{\n"

        # for i, exp in enumerate(self.exp_list):
        #     # Check if it's the last expression in the block
        #     if i == len(self.exp_list) - 1:
        #         break
        #     else:
        #         code += exp.build() + ";" + "\n"

        # # el codigo para q la ultima expression retorne es:
        # code += self.exp_list[-1].build()
        # last_newline_index = code.rfind("\n")

        # if last_newline_index != -1:
        #     substring_after_last_newline = code[last_newline_index + 1 :].lstrip()
        #     # print(substring_after_last_newline)
        #     code = (
        #         code[: last_newline_index + 1]
        #         + "return "
        #         + substring_after_last_newline
        #         + ";"
        #     )
        # else:
        #     code_without_initial_whitespace = code.lstrip()
        #     code = "return " + code_without_initial_whitespace + ";"
        # code += "\n}\n"
        # return code
        # endregion


class Let(Node):
    def __init__(self, assign, body):
        super().__init__(self, "LET")
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"let_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"let_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker

        self.assign = assign
        self.body = body

    def check(self):
        pass

    def infer_type(self):
        pass

    def build(self):  # generate c code
        self.static_type = "float"
        assign_def, assign_ret = self.assign[0].value.build()
        var_name = self.assign[0].name.name
        var_type = self.assign[0].name.static_type
        var_type = "float"  # temporal
        body_def, body_ret = self.body.build()
        self.ret_point = "ret_point_let_" + str(
            self.instance_id
        )  # analizar instance id

        c_code = f"""{self.static_type} let_{self.instance_id}(){{
        {assign_def}
        {var_type} {var_name} = {assign_ret};
        {body_def}
        return {body_ret};
        }}
        {self.static_type} {self.ret_point} = let_{self.instance_id}();
        """
        return c_code, self.ret_point

    # ret_point_3
    # region old
    # # Use instance_id to create a unique function name
    # c_code = f"{return_type} let_{self.instance_id}("
    # if len(self.assign) == 1:
    #     c_code += f"float {self.assign[0].name.name}"
    # else:
    #     for assignment in self.assign:
    #         c_code += f"float {assignment.name.name}, "
    #     c_code = c_code[:-2]
    # c_code += ") {\n"

    # # body
    # body_code = self.body.build()
    # # Sol (working)
    # if isinstance(self.body, ExpressionBlock):
    #     c_code += body_code
    #     c_code += "return " + self.body.name + "();"
    #     c_code += "\n}\n"
    # else:
    #     c_code += body_code
    #     last_newline_index = c_code.rfind("\n")
    #     if last_newline_index != -1:
    #         c_code = (
    #             c_code[: last_newline_index + 1]
    #             + "return "
    #             + c_code[last_newline_index + 1 :]
    #             + ";"
    #         )
    #         c_code += "\n}\n"
    #     else:
    #         raise ValueError(
    #             f"Te falto un salto de linea luego de algun {{ o de algun }} antes de llamar a la funcion"
    #         )

    # # arguments of the call
    # c_code += f"let_{self.instance_id}("
    # if len(self.assign) == 1:
    #     c_code += f"{self.assign[0].value}"
    # else:
    #     for assignment in self.assign:
    #         c_code += f"{assignment.value}, "
    #     c_code = c_code[:-2]
    # c_code += ")" + ("" if isinstance(self.parent, Let) else ";")
    # return c_code
    # endregion


class Assign(Node):  # example: name = var a ,value = 4
    def __init__(self, name, value):
        super().__init__(self, "ASSIGN")
        self.name = name
        self.value = value


class ID(Node):
    def __init__(self, name, opt_type):
        if opt_type == "":
            super().__init__(self, "var " + name)
        else:
            super().__init__(self, opt_type + " " + name)
        self.name = name
        self.opt_type = opt_type

    def infer_type(self):
        return self.opt_type

    def build(self):
        return "", self.name


class If(Node):
    def __init__(self, case_list):
        super().__init__(self, "IF")
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"if_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"if_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        self.case_list = case_list

    def build(self):
        self.static_type = "float"
        self.ret_point = "ret_point_if_" + str(self.instance_id)  # analizar id blabla
        c_code = f"""{self.static_type} if_{self.instance_id}(){{"""
        for case in self.case_list:
            def_case, ret_case = case.build()
            c_code += f"{def_case}"
            c_code += "\n"
        c_code += "}\n"
        c_code += f"{self.static_type} {self.ret_point} = if_{self.instance_id}();"
        return c_code, self.ret_point


class Case(Node):
    def __init__(self, condition, body, branch):
        super().__init__(self, "IF " + branch)
        self.condition = condition
        self.body = body
        self.branch = branch

    def build(self):

        c_code = ""
        def_condition, ret_condition = self.condition.build()
        def_body, ret_body = self.body.build()
        c_code += f"""{def_condition}"""
        c_code += f"""if ((int){ret_condition}){{
            {def_body}
            return {ret_body};
            }}"""
        return c_code, ""


class While(Node):
    def __init__(self, condition, body):
        super().__init__(self, "WHILE")
        self.condition = condition
        self.body = body


class For(Node):
    def __init__(self, iterator, iterable, body):
        super().__init__(self, "WHILE")
        self.iterator = iterator
        self.iterable = iterable
        self.body = body


class TrueLiteral(Node):
    def __init__(self):
        super().__init__(self, "TRUE")

    def build(self):
        return "", "1"


class FalseLiteral(Node):
    def __init__(self):
        super().__init__(self, "FALSE")

    def build(self):
        return "", "0"


class TypeDef(Node):
    def __init__(self, id, params, members, inherits):
        super().__init__(self, "TYPE_DEF")
        self.id = id
        self.variables = filter(lambda x: type(x) is Assign, members)
        self.functions = filter(lambda x: type(x) is FunctionDef, members)
        self.params = params
        self.inherits = inherits


class TypeCall(Node):
    def __init__(self, id, params):
        super().__init__(self, "TYPE_CALL")
        self.id = id
        self.params = params


class Protocol(Node):
    def __init__(self, id, methods, extends):
        super().__init__(self, "PROTOCOL")
        self.id = id
        self.methods = methods
        self.extends = extends


class VectorExt(Node):
    def __init__(self, items):
        super().__init__(self, "VECTOR_EXT")
        self.items = items


class VectorInt(Node):
    def __init__(self, expression, iterator, iterable):
        super().__init__(self, "VECTOR_INT")


class VectorCall(Node):
    def __init__(self, id, index):
        super().__init__(self, "VECTOR_CALL")
        self.id = id
        self.index = index


class BinOp(Node):
    
    def __init__(self, left, op, right):
        super().__init__(self, op)
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"bin_op_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"bin_op_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        self.left = left
        self.op = op
        self.right = right

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

    def build(self):
        self.static_type = "float"
        left_def, left_ret = self.left.build()
        right_def, right_ret = self.right.build()
        self.ret_point = "ret_point_bin_op_" + str(self.instance_id)

        code = f"""{self.static_type} bin_op_{self.instance_id}(){{
        {left_def}
        {right_def}"""
        if self.op in ["+", "-", "*", "/", "%"]:
            code += f"\nreturn (float)({left_ret} {self.op} {right_ret});\n"
        elif self.op in [">", "<", ">=", "<=", "==", "!="]:
            code += f"\nreturn (int)({left_ret} {self.op} {right_ret});\n"
        elif self.op in ["^", "**"]:
            code += f"\nreturn = (pow({left_ret}, {right_ret});\n"
        else:
            raise TypeError(f"Unknown operator {self.op}")
        code += "\n}\n"
        code += f"{self.static_type} {self.ret_point} = bin_op_{self.instance_id}();\n"
        return code, self.ret_point
        # elif self.op == "@":
        #     return f"(concatenate_strings({self.left.build()}, {self.right.build()}))"


class UnaryOp(Node):
    def __init__(self, op, operand):
        super().__init__(self, str(op))
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

    def build(self):
        if self.op == "-":
            return f"(-{self.operand.build()})"
        else:
            raise TypeError(f"Unknown unary operator {self.op}")


# number class
class Num(Node):
    def __init__(self, value):
        super().__init__(self, str(value))
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

    def build(self):
        return "", "(float)" + str(self.value)


class StringLiteral(Node):
    def __init__(self, value):
        super().__init__(self, value)
        # eliminate the ' ' from value
        if value[0] == "'" or value[0] == '"':
            value = value[1:-1]
        self.value = value

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
        super().__init__(self, "PI")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def build(self):
        return "M_PI"


class E(Node):

    def __init__(self):
        super().__init__(self, "E")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def build(self):
        return "M_E"


# endregion
# region built-in functions classes
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
        super().__init__(self, "PRINT")
        self.value = value

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def build(self):
        child_def, child_ret = self.value.build()
        self.static_type = "float"
        self.ret_point = "ret_point_print_" + str(self.instance_id)
        code = f"""{self.static_type} print_{self.instance_id}() {{
{child_def}

printf("%f\\n",{child_ret});
return {child_ret};
}}
{self.static_type} {self.ret_point} = print_{self.instance_id}();
"""
        return code, self.ret_point


class Sqrt(Node):
    def __init__(self, value):
        super().__init__(self, "SQRT")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")
        if self.value.eval() < 0:
            raise ValueError("sqrt of a negative number")

    def infer_type(self):
        return "number"

    def build(self):
        return f"sqrt({self.value.build()})"


class Sin(Node):
    def __init__(self, value):
        super().__init__(self, "SIN")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def build(self):
        return f"sin({self.value.build()})"


class Cos(Node):
    def __init__(self, value):
        super().__init__(self, "COS")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def build(self):
        return f"cos({self.value.build()})"


class Exp(Node):
    def __init__(self, value):
        super().__init__(self, "EXP")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def build(self):
        return f"exp({self.value.build()})"


class Log(Node):
    def __init__(self, value, base):
        super().__init__(self, "LOG")
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
        if not (self.base.value > 0 and self.base.value != 1):
            raise ValueError(
                "Logarithm base must be greater than 0 and not equal to 1."
            )
        if self.value.value <= 0:
            raise ValueError("Logarithm argument must be greater than 0.")

    def infer_type(self):
        return "number"

    def build(self):
        return f"(log({self.value.build()}) / log({self.base.build()}))"


class Rand(Node):

    def __init__(self):
        super().__init__(self, "RAND")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def build(self):
        # Using rand() from stdlib.h, scaled to 0-1 range
        return f"((float)rand() / (float)RAND_MAX)"


# endregion
# region precedence rules for the arithmetic operators

# region GRAMMAR

precedence = (
    #("right", "PRINT","SQRT","SIN","COS","EXP","LOG","RAND"),
    ("right", "LET", "IN"),
    ("right", "IF", "ELIF", "ELSE"),
    ("right", "WHILE", "FOR"),
    ("nonassoc", "EQUAL"),
    ("right", "ASSDESTROYER"),
    ("left", "AS"),
    ("left", "IS"),
    ("left", "CONCAT", "DCONCAT"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQEQUAL","NOTEQUAL"),
    ("nonassoc", "LESSEQUAL","GREATEREQUAL","LESS","GREATER"),
    ("right", "NOT"),
    # ("right", "PRINT","SQRT","SIN","COS","EXP","LOG","RAND"),
    ("right", "LET", "IN"),
    ("right", "IF", "ELIF", "ELSE"),
    ("right", "WHILE", "FOR"),
    ("nonassoc", "EQUAL"),
    ("right", "ASSDESTROYER"),
    ("left", "AS"),
    ("left", "IS"),
    ("left", "CONCAT", "DCONCAT"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQEQUAL", "NOTEQUAL"),
    ("nonassoc", "LESSEQUAL", "GREATEREQUAL", "LESS", "GREATER"),
    ("right", "NOT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "POWER"),
    ("right", "UMINUS"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "NAME"),
    ("left", "DOT"),
    ("nonassoc", "NAME"),
    ("left", "DOT"),
)
# endregion
# region Defining the Grammatic


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
    "program : functions_types_protocols global_hl_expression"
    p[0] = Program(p[1], p[2])
    for i in p[1]:
        i.parent = p[0]
    if p[2]:
        p[2].parent = p[0]


def p_global_hl_expression(p):
    "global_hl_expression : hl_expression"
    p[0] = p[1]

def p_global_hl_expression_e(p):
    "global_hl_expression : empty"
    p[0] = None

def p_functionsx_types_protocols_list_items(p):
    "functions_types_protocols : function_def functions_types_protocols"
    p[0] = [p[1]]+p[2]

def p_functions_typesx_protocols_list_items(p):
    "functions_types_protocols : type_def functions_types_protocols"
    p[0] = [p[1]]+p[2]

def p_functions_types_protocolsx_list_items(p):
    "functions_types_protocols : protocol_def functions_types_protocols"
    p[0] = [p[1]]+p[2]

def p_function_type_list_items_empty(p):
    "functions_types_protocols : empty"
    p[0]=[]

def p_protocol(p):
    "protocol_def : PROTOCOL NAME opt_extends LBRACE protocol_methods RBRACE opt_semi"
    id = ID(p[2], "protocol")
    p[0] = Protocol(id, p[5], p[3])
    id.parent = p[0]
    for i in p[5]:
        i.parent = p[0]
    if p[3]:
        p[3].parent = p[0]

def p_protocol_extends(p):
    "opt_extends : EXTENDS NAME"
    p[0] = ID(p[2], "extends")

def p_protocol_extends_e(p):
    "opt_extends : empty"
    p[0] = None

def p_protocol_methods(p):
    "protocol_methods : protocol_method protocol_methods"
    p[0] = [p[1]]+p[2]

def p_protocol_methods_e(p):
    "protocol_methods : protocol_method empty"
    p[0] = [p[1]]

def p_protocol_method(p):
    "protocol_method : NAME LPAREN protocol_method_params RPAREN COLON NAME SEMI"
    id = ID(p[1], p[6])
    params = Params(p[3])
    for i in p[3]:
        i.parent = params
    p[0] = FunctionDef(id, params, None)
    id.parent = p[0]
    params.parent = p[0]

def p_protocol_method_params(p):
    "protocol_method_params : NAME COLON NAME protocol_method_params_rem"
    p[0] = [ID(p[1], p[3])]+p[4]

def p_protocol_method_params_e(p):
    "protocol_method_params : empty"
    p[0] = []

def p_protocol_method_params_rem(p):
    "protocol_method_params_rem : COMMA NAME COLON NAME protocol_method_params_rem"
    p[0] = [ID(p[2], p[4])]+p[5]

def p_protocol_method_params_rem_e(p):
    "protocol_method_params_rem : empty"
    p[0] = []


def p_exp_func_call(p):
    "expression : func_call"
    p[0] = p[1]


def p_func_call(p):
    "func_call : NAME LPAREN cs_exps RPAREN"
    id = ID(p[1],"func_call")
    p[0] = FunctionCall(id,p[3])
    id.parent = p[0]
    p[3].parent = p[0]

def p_exp_type_call(p):
    "expression : type_call"
    p[0]=p[1]

def p_type_call(p):
    "type_call : NEW NAME LPAREN cs_exps RPAREN"
    id = ID(p[2], p[2])
    p[0] = TypeCall(id,p[4])
    id.parent = p[0]
    p[4].parent = p[0]

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
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type INLINE hl_expression"
    id = ID(p[2],p[6])
    p[0] = FunctionDef(id,p[4],p[8])
    id.parent = p[0]
    p[4].parent = p[0]
    p[8].parent = p[0]


def p_function_def_fullform(p):
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type expression_block opt_semi"
    id = ID(p[2],p[6])
    p[0] = FunctionDef(id,p[4],p[7])
    id.parent = p[0]
    p[4].parent = p[0]
    p[7].parent = p[0]


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

def p_type_def(p):
    "type_def : TYPE NAME opt_type_params opt_inheritance LBRACE type_members RBRACE opt_semi"
    params = Params(p[3])
    for i in p[3]:
        i.parent = params

    id = ID(p[2], p[2])

    p[0] = TypeDef(id, params, p[6], p[4])
    for i in p[6]:
        i.parent = p[0]
    params.parent = p[0]
    id.parent = p[0]
    if p[4]:
        p[4].parent = p[0]

def p_opt_inheritance(p):
    "opt_inheritance : INHERITS NAME opt_inheritance_params"
    id = ID(p[2], "inherits")
    p[0] = TypeCall(id, p[3])
    p[3].parent = p[0]
    id.parent = p[0]

def p_opt_inheritance_e(p):
    "opt_inheritance : empty"
    p[0] = None

def p_opt_inheritance_params(p):
    "opt_inheritance_params : LPAREN cs_exps RPAREN"
    p[0] = p[2]

def p_opt_inheritance_params_e(p):
    "opt_inheritance_params : empty"
    p[0] = Params([])

def p_opt_type_params(p):
    "opt_type_params : LPAREN typedef_params RPAREN"
    p[0] = p[2]

def p_opt_type_params_e(p):
    "opt_type_params : empty"
    p[0] = []

def p_typedef_params(p):
    "typedef_params : namedef typedef_params_rem"
    p[0] = [p[1]]+p[2]

def p_typedef_params_e(p):
    "typedef_params : empty"
    p[0] = []

def p_typedef_params_rem(p):
    "typedef_params_rem : COMMA namedef typedef_params_rem"
    p[0] = [p[2]] + p[3]

def p_typedef_params_rem_e(p):
    "typedef_params_rem : empty"
    p[0] = []

def p_type_members(p):
    "type_members : type_member type_members"
    p[0] = [p[1]]+p[2]

def p_type_members_e(p):
    "type_members : empty"
    p[0] = []

def p_member_func(p):
    "type_member : member_func"
    p[0] = p[1]

def p_member_function_def(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type INLINE hl_expression"
    id = ID(p[1],p[5])
    p[0] = FunctionDef(id,p[3],p[7])
    id.parent = p[0]
    p[3].parent = p[0]
    p[7].parent = p[0]

def p_member_function_def_fullform(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type expression_block opt_semi"
    id = ID(p[1],p[5])
    p[0] = FunctionDef(id,p[3],p[6])
    id.parent = p[0]
    p[3].parent = p[0]
    p[6].parent = p[0]

def p_member_var(p):
    "type_member : member_var"
    p[0] = p[1]

def p_member_var_dec(p):
    "member_var : namedef EQUAL hl_expression"
    p[0] = Assign(p[1], p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]

def p_global_hl_expression_e(p):
    "global_hl_expression : empty"
    p[0] = None


def p_functionsx_types_protocols_list_items(p):
    "functions_types_protocols : function_def functions_types_protocols"
    p[0] = [p[1]] + p[2]


def p_functions_typesx_protocols_list_items(p):
    "functions_types_protocols : type_def functions_types_protocols"
    p[0] = [p[1]] + p[2]


def p_functions_types_protocolsx_list_items(p):
    "functions_types_protocols : protocol_def functions_types_protocols"
    p[0] = [p[1]] + p[2]


def p_function_type_list_items_empty(p):
    "functions_types_protocols : empty"
    p[0] = []


def p_protocol(p):
    "protocol_def : PROTOCOL NAME opt_extends LBRACE protocol_methods RBRACE opt_semi"
    id = ID(p[2], "protocol")
    p[0] = Protocol(id, p[5], p[3])
    id.parent = p[0]
    for i in p[5]:
        i.parent = p[0]
    if p[3]:
        p[3].parent = p[0]


def p_protocol_extends(p):
    "opt_extends : EXTENDS NAME"
    p[0] = ID(p[2], "extends")


def p_protocol_extends_e(p):
    "opt_extends : empty"
    p[0] = None


def p_protocol_methods(p):
    "protocol_methods : protocol_method protocol_methods"
    p[0] = [p[1]] + p[2]


def p_protocol_methods_e(p):
    "protocol_methods : protocol_method empty"
    p[0] = [p[1]]


def p_protocol_method(p):
    "protocol_method : NAME LPAREN protocol_method_params RPAREN COLON NAME SEMI"
    id = ID(p[1], p[6])
    params = Params(p[3])
    for i in p[3]:
        i.parent = params
    p[0] = FunctionDef(id, params, None)
    id.parent = p[0]
    params.parent = p[0]


def p_protocol_method_params(p):
    "protocol_method_params : NAME COLON NAME protocol_method_params_rem"
    p[0] = [ID(p[1], p[3])] + p[4]


def p_protocol_method_params_e(p):
    "protocol_method_params : empty"
    p[0] = []


def p_protocol_method_params_rem(p):
    "protocol_method_params_rem : COMMA NAME COLON NAME protocol_method_params_rem"
    p[0] = [ID(p[2], p[4])] + p[5]


def p_protocol_method_params_rem_e(p):
    "protocol_method_params_rem : empty"
    p[0] = []


def p_exp_func_call(p):
    "expression : func_call"
    p[0] = p[1]


def p_func_call(p):
    "func_call : NAME LPAREN cs_exps RPAREN"
    id = ID(p[1], "func_call")
    p[0] = FunctionCall(id, p[3])
    id.parent = p[0]
    p[3].parent = p[0]


def p_exp_type_call(p):
    "expression : type_call"
    p[0] = p[1]


def p_type_call(p):
    "type_call : NEW NAME LPAREN cs_exps RPAREN"
    id = ID(p[2], p[2])
    p[0] = TypeCall(id, p[4])
    id.parent = p[0]
    p[4].parent = p[0]


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
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type INLINE hl_expression"
    id = ID(p[2], p[6])
    p[0] = FunctionDef(id, p[4], p[8])
    id.parent = p[0]
    p[4].parent = p[0]
    p[8].parent = p[0]


def p_function_def_fullform(p):
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type expression_block opt_semi"
    id = ID(p[2], p[6])
    p[0] = FunctionDef(id, p[4], p[7])
    id.parent = p[0]
    p[4].parent = p[0]
    p[7].parent = p[0]


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


def p_type_def(p):
    "type_def : TYPE NAME opt_type_params opt_inheritance LBRACE type_members RBRACE opt_semi"
    params = Params(p[3])
    for i in p[3]:
        i.parent = params

    id = ID(p[2], p[2])

    p[0] = TypeDef(id, params, p[6], p[4])
    for i in p[6]:
        i.parent = p[0]
    params.parent = p[0]
    id.parent = p[0]
    if p[4]:
        p[4].parent = p[0]


def p_opt_inheritance(p):
    "opt_inheritance : INHERITS NAME opt_inheritance_params"
    id = ID(p[2], "inherits")
    p[0] = TypeCall(id, p[3])
    p[3].parent = p[0]
    id.parent = p[0]


def p_opt_inheritance_e(p):
    "opt_inheritance : empty"
    p[0] = None


def p_opt_inheritance_params(p):
    "opt_inheritance_params : LPAREN cs_exps RPAREN"
    p[0] = p[2]


def p_opt_inheritance_params_e(p):
    "opt_inheritance_params : empty"
    p[0] = Params([])


def p_opt_type_params(p):
    "opt_type_params : LPAREN typedef_params RPAREN"
    p[0] = p[2]


def p_opt_type_params_e(p):
    "opt_type_params : empty"
    p[0] = []


def p_typedef_params(p):
    "typedef_params : namedef typedef_params_rem"
    p[0] = [p[1]] + p[2]


def p_typedef_params_e(p):
    "typedef_params : empty"
    p[0] = []


def p_typedef_params_rem(p):
    "typedef_params_rem : COMMA namedef typedef_params_rem"
    p[0] = [p[2]] + p[3]


def p_typedef_params_rem_e(p):
    "typedef_params_rem : empty"
    p[0] = []


def p_type_members(p):
    "type_members : type_member type_members"
    p[0] = [p[1]] + p[2]


def p_type_members_e(p):
    "type_members : empty"
    p[0] = []


def p_member_func(p):
    "type_member : member_func"
    p[0] = p[1]


def p_member_function_def(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type INLINE hl_expression"
    id = ID(p[1], p[5])
    p[0] = FunctionDef(id, p[3], p[7])
    id.parent = p[0]
    p[3].parent = p[0]
    p[7].parent = p[0]


def p_member_function_def_fullform(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type expression_block opt_semi"
    id = ID(p[1], p[5])
    p[0] = FunctionDef(id, p[3], p[6])
    id.parent = p[0]
    p[3].parent = p[0]
    p[6].parent = p[0]


def p_member_var(p):
    "type_member : member_var"
    p[0] = p[1]


def p_member_var_dec(p):
    "member_var : namedef EQUAL hl_expression"
    p[0] = Assign(p[1], p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_tbl(p):
    """expression : expression_block"""
    p[0] = p[1]


def p_hl_expression(p):
    """hl_expression : expression SEMI
    | expression_block
    """
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
#     """expression_block_hl : LBRACE expression_block_list RBRACE"""
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


def p_if_hl(p):
    "hl_expression : IF expression_parenthized expression opt_elifs ELSE hl_expression"
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].case_list:
        i.parent = p[0]


def p_if_exp(p):
    "expression : IF expression_parenthized expression opt_elifs ELSE expression"
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].case_list:
        i.parent = p[0]


def p_opt_elifs(p):
    "opt_elifs : ELIF expression_parenthized expression opt_elifs"
    elif_cond = Case(p[2], p[3], "elif")
    p[2].parent = elif_cond
    p[3].parent = elif_cond
    p[0] = [elif_cond] + p[4]


def p_opt_elifs_e(p):
    "opt_elifs : empty"
    p[0] = []


def p_opt_semi(p):
    """opt_semi : SEMI
    | empty"""


def p_for_hl(p):
    "hl_expression : FOR LPAREN destroyable IN expression RPAREN hl_expression"
    p[0] = For(p[3], p[5], p[7])
    p[3].parent = p[0]
    p[5].parent = p[0]
    p[7].parent = p[0]


def p_for(p):
    "expression : FOR LPAREN destroyable IN expression RPAREN expression"
    p[0] = For(p[3], p[5], p[7])
    p[3].parent = p[0]
    p[5].parent = p[0]
    p[7].parent = p[0]


def p_while_hl(p):
    "hl_expression : WHILE expression_parenthized hl_expression"
    p[0] = While(p[2], p[3])
    p[2].parent = p[0]
    p[3].parent = p[0]


def p_while(p):
    "expression : WHILE expression_parenthized expression"
    p[0] = While(p[2], p[3])
    p[2].parent = p[0]
    p[3].parent = p[0]


def p_expression_group(p):
    "expression : expression_parenthized"
    p[0] = p[1]


def p_expression_parenthized(p):
    "expression_parenthized : LPAREN expression RPAREN"
    p[0] = p[2]
# endregion
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
    | destroyable ASSDESTROYER expression
    | member_resolute ASSDESTROYER expression
    | expression IS type_test
    | expression AS type_test
    """
    if p[2] == ":=":
        p[0] = BinOp(left=p[1], op="AD", right=p[3])
    else:
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
    | destroyable ASSDESTROYER hl_expression
    | member_resolute ASSDESTROYER hl_expression
    """
    if p[2] == ":=":
        p[0] = BinOp(left=p[1], op="AD", right=p[3])
    else:
        p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_destroyable(p):
    "destroyable : NAME"
    p[0] = ID(p[1], "")


def p_type_test(p):
    "type_test : NAME"
    p[0] = ID(p[1], p[1])


def p_exp_member_resolute(p):
    "expression : member_resolute"
    p[0] = p[1]


def p_member_resolute(p):
    "member_resolute : expression DOT member_resolut"
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_member_resolut_fc(p):
    "member_resolut : func_call"
    p[0] = p[1]


def p_member_resolut_att(p):
    "member_resolut : NAME"
    p[0] = ID(p[1], "")


def p_expression_unary(p):
    """expression : NOT expression
    | MINUS expression %prec UMINUS"""
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_unary_hl(p):
    """hl_expression : NOT hl_expression
    | MINUS hl_expression %prec UMINUS"""
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


def p_expression_vector(p):
    "expression : vector"
    p[0] = p[1]


def p_vector_ext(p):
    "vector : LSQB cs_exps RSQB"
    p[0] = VectorExt(p[2])
    p[2].parent = p[0]


def p_vector_int(p):
    "vector : LSQB expression SUCH_AS destroyable IN expression RSQB"
    p[0] = VectorInt(p[2], p[4], p[6])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[6].parent = p[0]


def p_expression_vector_ind_pare(p):
    "expression :  expression LSQB expression RSQB"
    p[0] = VectorCall(p[1], p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


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
    sErrorList.append(p)
    # print(sErrorList[-1])


# endregion


def p_error(p):
    sErrorList.append(p)
    # print(sErrorList[-1])


# endregion

# region Generate AST


def find_column(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    if line_start < 0:
        line_start = 0
    return (token.lexpos - line_start) + 1


def hulk_parse(code):

    parser = yacc.yacc(start="program", method="LALR")

    AST = parser.parse(code)

    if len(sErrorList) == 0:

        try:
            create_AST_graph(nodes, "AST")
        except Exception as e:
            print("NO SE PUDO CREAR EL GRAFO....muy grande!!!")
            print(e)
        return AST
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
            break

        return None


# create output.c file with the code transformed

if __name__ == "__main__":
    ast = hulk_parse(r"function fact(a){if(a>0) a*fact(a-1) else 1;}print(fact(5));")
    # ast = hulk_parse(r"print(2>1);")
    ast.build()
# endregion
# xd
