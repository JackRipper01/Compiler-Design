import node_classes as nc
import math

# constants
PI = math.pi
E = math.e

# Generate C code from AST
def generate_c_code(node):
    if isinstance(node, nc.BinOp) and node.op in ["+", "-", "*", "/"]:
        return f"({generate_c_code(node.left)} {node.op} {generate_c_code(node.right)})"
    elif isinstance(node, nc.BinOp) and node.op in ["^", "**"]:
        return f"pow({generate_c_code(node.left)}, {generate_c_code(node.right)})"
    elif isinstance(node, nc.BinOp) and node.op == "@":
        # Handle the '@' operation for concatenation
        left_code = generate_c_code(node.left)
        right_code = generate_c_code(node.right)
        # Assuming all operands are converted to strings
        return f"(strcat({left_code}, {right_code}))"
    elif isinstance(node, nc.Num):
        return str(node.value)
    elif isinstance(node, nc.StringLiteral):
        return f'"{node.value}"'
    elif isinstance(node, nc.UnaryOp):
        return f"{node.op}{generate_c_code(node.operand)}"
    elif isinstance(node, nc.Print):
        return f'printf("%f\\n", {generate_c_code(node.value)})'
    elif isinstance(node, nc.Pi):
        return "M_PI"
    elif isinstance(node, E):
        return "M_E"
    elif isinstance(node, nc.Sqrt):
        return f"sqrt({generate_c_code(node.value)})"
    elif isinstance(node, nc.Sin):
        return f"sin({generate_c_code(node.value)})"
    elif isinstance(node, nc.Cos):
        return f"cos({generate_c_code(node.value)})"
    elif isinstance(node, nc.Exp):
        return f"exp({generate_c_code(node.value)})"
    elif isinstance(node, nc.Log):
        return f"(log({generate_c_code(node.base)}) / log({generate_c_code(node.value)}))"  # logaritmo se hace asi pq C no admite log de a en base b
    elif isinstance(node, nc.Rand):
        return "((float) rand() / (RAND_MAX))"
    else:
        raise TypeError(f"Unknown node {node}")


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    c_code = generate_c_code(ast)
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <math.h>\n")
        f.write("#include <stdlib.h>\n")
        f.write("#include <string.h>\n\n")

        f.write("int main() {\n")
        f.write(f"    {c_code};\n")
        f.write("    return 0;\n")
        f.write("}\n")
