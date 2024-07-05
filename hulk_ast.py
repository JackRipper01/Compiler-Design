nodes = {}
global_definitions = {}

class Node:
    def __init__(self, slf, nm):
        nodes[slf] = nm
        self.parent : Node = None
        self.static_type = "Object"
        self.ret_point = "ret_point"
        self.variable_scope = {}
        self.global_definitions = global_definitions


class Program(Node):
    function_names = set()  # Class variable to keep track of function names
    instance_count = 0

    def __init__(self, functions_types, global_expression):
        super().__init__(self, "PROGRAM")
        self.functions = list(filter(lambda x: type(x) is FunctionDef, functions_types))
        self.types = list(filter(lambda x: type(x) is TypeDef, functions_types))
        self.protocols = list(filter(lambda x: type(x) is Protocol, functions_types))
        self.global_exp: Node = global_expression

    @classmethod
    def add_function_name(cls, name):
        if name in cls.function_names:
            raise ValueError(f"Function {name} is already defined.")
        cls.function_names.add(name)

    @classmethod
    def function_name_exists(cls, name):
        return name in cls.function_names


# region FunctionClasses
class FunctionDef(Node):
    def __init__(self, func_id, params, body):
        super().__init__(self, "FUNC_DEF")
        self.func_id : ID = func_id
        self.params : Params = params
        self.body : Node = body
        # Check if the function name already exists
        if Program.function_name_exists(self.func_id):
            raise ValueError(f"Function {self.func_id} is already defined.")
        Program.add_function_name(self.func_id)  # Add the function name to the tracker


class FunctionCall(Node):
    def __init__(self, func_id, params):
        super().__init__(self, "FUNC_CALL")
        self.func_id : ID = func_id
        self.params : Params = params


class Params(Node):
    def __init__(self, param_list):
        super().__init__(self, "params")
        self.param_list = param_list


# endregion
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

        self.assign : Assign = assign
        self.body : Node = body


class Assign(Node):  # example: name = var a ,value = 4
    def __init__(self, name, value):
        super().__init__(self, "ASSIGN")
        self.name : ID = name
        self.value : Node = value


class ID(Node):
    def __init__(self, name, annotated_type):
        if annotated_type == "":
            super().__init__(self, "var " + name)
        else:
            super().__init__(self, annotated_type + " " + name)
        self.name:str = name
        self.annotated_type :str = annotated_type


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


class Case(Node):
    def __init__(self, condition, body, branch):
        super().__init__(self, "IF " + branch)
        self.condition:Node = condition
        self.body : Node = body
        self.branch = branch


class While(Node):
    def __init__(self, condition, body):
        super().__init__(self, "WHILE")
        self.condition: Node = condition
        self.body : Node = body
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"while_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"while_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker


class For(Node):
    def __init__(self, iterator, iterable, body):
        super().__init__(self, "FOR")
        self.iterator: ID = iterator
        self.iterable: Node = iterable
        self.body : Node = body


class TrueLiteral(Node):
    def __init__(self):
        super().__init__(self, "TRUE")


class FalseLiteral(Node):
    def __init__(self):
        super().__init__(self, "FALSE")


class TypeDef(Node):
    def __init__(self, id, params, members, inherits):
        super().__init__(self, "TYPE_DEF")
        self.id : ID = id 
        self.variables = list(filter(lambda x: type(x) is Assign, members))
        self.functions = list(filter(lambda x: type(x) is FunctionDef, members))
        self.params : Params = params
        self.inherits : TypeCall = inherits


class TypeCall(Node):
    def __init__(self, id, params):
        super().__init__(self, "TYPE_CALL")
        self.id : ID = id
        self.params : Params = params


# region temporal
class Protocol(Node):
    def __init__(self, id, methods, extends):
        super().__init__(self, "PROTOCOL")
        self.id : ID = id
        self.methods = methods
        self.extends : ID = extends


class VectorExt(Node):
    def __init__(self, items):
        super().__init__(self, "VECTOR_EXT")
        self.items = items


class VectorInt(Node):
    def __init__(self, expression, iterator, iterable):
        super().__init__(self, "VECTOR_INT")
        self.expression : Node = expression
        self.iterator : ID = iterator
        self.iterable : Node = iterable


class VectorCall(Node):
    def __init__(self, id, index):
        super().__init__(self, "VECTOR_CALL")
        self.id : Node = id
        self.index : Node = index


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
        super().__init__(self, op)
        Program.instance_count += 1  # Increment the counter for each new instance
        self.instance_id = Program.instance_count
        self.name = f"bin_op_{self.instance_id}"
        while Program.function_name_exists(self.name):
            Program.instance_count += 1
            self.instance_id = Program.instance_count
            self.name = f"bin_op_{self.instance_id}"
        Program.add_function_name(self.name)  # Add the function name to the tracker
        self.left : Node = left
        self.op : str = op
        self.right :Node = right


class UnaryOp(Node):
    def __init__(self, op, operand):
        super().__init__(self, str(op))
        self.op = op
        self.operand : Node = operand


class Num(Node):
    def __init__(self, value):
        super().__init__(self, str(value))
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value


class StringLiteral(Node):
    def __init__(self, value):
        super().__init__(self, value)
        # eliminate the ' ' from value
        if value[0] == "'" or value[0] == '"':
            value = value[1:-1]
        self.value = value


class Pi(Node):

    def __init__(self):
        super().__init__(self, "PI")


class E(Node):

    def __init__(self):
        super().__init__(self, "E")


# region built-in functions
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
        self.value : Node = value


class Sqrt(Node):
    def __init__(self, value):
        super().__init__(self, "SQRT")
        self.value : Node = value


class Sin(Node):
    def __init__(self, value):
        super().__init__(self, "SIN")
        self.value : Node = value


class Cos(Node):
    def __init__(self, value):
        super().__init__(self, "COS")
        self.value : Node = value


class Exp(Node):
    def __init__(self, value):
        super().__init__(self, "EXP")
        self.value : Node = value


class Log(Node):
    def __init__(self, value, base):
        super().__init__(self, "LOG")
        self.base : Node = base
        self.value : Node = value


class Rand(Node):

    def __init__(self):
        super().__init__(self, "RAND")
