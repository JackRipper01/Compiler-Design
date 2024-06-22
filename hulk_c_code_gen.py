import hulk_parser

# Generate C code from AST
def generate_c_code(node):
    if isinstance(node, hulk_parser.BinOp):
        return f"({generate_c_code(node.left)} {node.op} {generate_c_code(node.right)})"
    elif isinstance(node, hulk_parser.Num):
        return str(node.value)
    elif isinstance(node, hulk_parser.UnaryOp):
        return f"{node.op}{generate_c_code(node.operand)}"
    elif isinstance(node, hulk_parser.Print):
        return f'printf("%f\\n", {generate_c_code(node.value)})'
    elif isinstance(node, hulk_parser.Pi):
        return "M_PI"
    elif isinstance(node, hulk_parser.E):
        return "M_E"
    elif isinstance(node, hulk_parser.Sqrt):
        return f"sqrt({generate_c_code(node.value)})"
    elif isinstance(node, hulk_parser.Sin):
        return f"sin({generate_c_code(node.value)})"
    elif isinstance(node, hulk_parser.Cos):
        return f"cos({generate_c_code(node.value)})"
    elif isinstance(node, hulk_parser.Exp):
        return f"exp({generate_c_code(node.value)})"
    elif isinstance(node, hulk_parser.Log):
        return f"(log({generate_c_code(node.base)}) / log({generate_c_code(node.value)}))"  # logaritmo se hace asi pq C no admite log de a en base b
    elif isinstance(node, hulk_parser.Rand):
        return "((double) rand() / (RAND_MAX))"
    else:
        raise TypeError(f"Unknown node {node}")


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    c_code = generate_c_code(ast)
    with open(filename, "w") as f:
        f.write("#include <stdio.h>\n")
        f.write("#include <math.h>\n")
        f.write("#include <stdlib.h>\n\n")
        f.write("int main() {\n")
        f.write(f"    {c_code};\n")
        f.write("    return 0;\n")
        f.write("}\n")