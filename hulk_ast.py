nodes = {}

class Node:
    def __init__(self, slf, nm):
        nodes[slf] = nm
        self.parent = None
        self.static_type = "Object"
        self.dynamic_type = "Object"
        self.ret_point = "ret_point"
        self.variable_scope = {}
        self.function_type_prototype_scope = {}

    def check(self):
        "check the correct use of the variables in the current scope"
        pass

    def infer_type(self):
        "tries to infer the type of the current expression"
        pass

    def build(self):
        "generates the code for the "
        pass


class Program(Node):
    function_names = set()  # Class variable to keep track of function names
    instance_count = 0

    def __init__(self, functions_types, global_expression):
        super().__init__(self, "PROGRAM")
        self.functions = filter(lambda x: type(x) is FunctionDef, functions_types)
        self.types = filter(lambda x: type(x) is TypeDef, functions_types)
        self.global_exp = global_expression

    def build(self):
        main_def, main_ret = self.global_exp.build()
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
            f.write(f"{main_def}\n\n")
            f.write(f"return {main_ret};\n")
            f.write("}\n")

    @classmethod
    def add_function_name(cls, name):
        if name in cls.function_names:
            raise ValueError(f"Function {name} is already defined.")
        cls.function_names.add(name)

    @classmethod
    def function_name_exists(cls, name):
        return name in cls.function_names


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


class Assign(Node):  # example: name = var a ,value = 4
    def __init__(self, name, value):
        super().__init__(self, "ASSIGN")
        self.name = name
        self.value = value


class ID(Node):
    def __init__(self, name, annotated_type):
        if annotated_type == "":
            super().__init__(self, "var " + name)
        else:
            super().__init__(self, annotated_type + " " + name)
        self.name = name
        self.annotated_type = annotated_type

    def infer_type(self):
        return self.annotated_type

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
        super().__init__(self, "FOR")
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

