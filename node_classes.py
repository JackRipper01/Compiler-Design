from typing import Self

import math
import random

# constants
PI = math.pi
E = math.e

from graphviz import Digraph

# region classes##################################
class Node:

    def __init__(self):
        self.graph = Digraph("AST", node_attr={"shape": "box"})
        self.id = ""

    def graphviz(self, parent_name):
        pass

    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass


# Operations Classes (binary, unary,etc)
class BinOp(Node):

    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

    def graphviz(self, parent_name):
        left_name = f"{parent_name}_left"
        right_name = f"{parent_name}_right"
        self.graph.node(left_name, label=str(self.left))
        self.graph.node(right_name, label=str(self.right))
        self.graph.edge(parent_name, left_name, label=self.op)
        self.graph.edge(parent_name, right_name, label=self.op)
        self.left.graphviz(left_name)
        self.right.graphviz(right_name)

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


class UnaryOp(Node):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op
        self.operand = operand

    def __str__(self):
        return f"UnaryOp({self.op}, {self.operand})"

    def graphviz(self, parent_name):
        operand_name = f"{parent_name}_operand"
        self.graph.node(operand_name, label=str(self.operand))
        self.graph.edge(parent_name, operand_name, label=self.op)
        self.operand.graphviz(operand_name)

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
        super().__init__()
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value

    def __str__(self):
        return str(self.value)

    def graphviz(self, parent_name):
        self.graph.node(parent_name, label=str(self.value))

    def check(self):
        # Check that the value is a number
        if not isinstance(self.value, (float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        # The type of a number is 'num'
        return "number"

    def eval(self):
        return self.value


class StringLiteral(Node):
    def __init__(self, value):
        super().__init__()
        # eliminate the ' ' from value
        if value[0] == "'" or value[0] == '"':
            value = value[1:-1]
        self.value = value

    def __str__(self):
        return str(self.value)

    def graphviz(self, parent_name):
        self.graph.node(parent_name, label=str(self.value))

    def check(self):
        pass

    def infer_type(self):
        return "string"

    def eval(self):
        return self.value


# constants classes
class Pi(Node):

    def __str__(self):
        return "Pi"

    def graphviz(self, parent_name):
        self.graph.node(parent_name, label="Pi")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return PI


class E(Node):

    def __str__(self):
        return "E"

    def graphviz(self, parent_name):
        self.graph.node(parent_name, label="E")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return E


# endregion
# region built-in functions classes########################
class Print(
    Node
):  # most be modified to work with all literals, now only works with numbers, missing strings and booleans
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Print({self.value})"

    def graphviz(self, parent_name):
        value_name = f"{parent_name}_value"
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, value_name, label="print")
        self.value.graphviz(value_name)

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def eval(self):
        print(self.value.eval())


class Sqrt(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Sqrt({self.value})"

    def graphviz(self, parent_name):
        value_name = f"{parent_name}_value"
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, value_name, label="sqrt")
        self.value.graphviz(value_name)

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
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Sin({self.value})"

    def graphviz(self, parent_name):
        value_name = f"{parent_name}_value"
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, value_name, label="sin")
        self.value.graphviz(value_name)

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
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Cos({self.value})"

    def graphviz(self, parent_name):
        value_name = f"{parent_name}_value"
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, value_name, label="cos")
        self.value.graphviz(value_name)

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
        super().__init__()
        self.value = value

    def __str__(self):
        return f"Exp({self.value})"

    def graphviz(self, parent_name):
        value_name = f"{parent_name}_value"
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, value_name, label="exp")
        self.value.graphviz(value_name)

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
        super().__init__()
        self.base = base
        self.value = value

    def __str__(self):
        return f"Log({self.base}, {self.value})"

    def graphviz(self, parent_name):
        base_name = f"{parent_name}_base"
        value_name = f"{parent_name}_value"
        self.graph.node(base_name, label=str(self.base))
        self.graph.node(value_name, label=str(self.value))
        self.graph.edge(parent_name, base_name, label="log")
        self.graph.edge(parent_name, value_name, label="log")
        self.base.graphviz(base_name)
        self.value.graphviz(value_name)

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

    def __str__(self):
        return "Rand"

    def graphviz(self, parent_name):
        self.graph.node(parent_name, label="Rand")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return random.uniform(0, 1)


# endregion
