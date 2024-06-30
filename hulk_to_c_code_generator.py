from hulk_parser import (
    Node,
    Program,
    FunctionList,
    FunctionDef,
    FunctionCall,
    Params,
    ExpressionBlock,
    Let,
    Assign,
    ID,
    If,
    Case,
    While,
    For,
    TrueLiteral,
    FalseLiteral,
    TypeDef,
    TypeCall,
    Protocol,
    VectorExt,
    VectorInt,
    VectorCall,
    BinOp,
    UnaryOp,
    Num,
    StringLiteral,
    Pi,
    E,
    Print,
    Sqrt,
    Sin,
    Cos,
    Exp,
    Log,
    Rand,
    hulk_parse,
)

ast = hulk_parse(r"print(let a = 5 in let b=4 in print(a));")


# create output.c file with the code transformed
def write_c_code_to_file(ast, filename):
    code_main = ast.build()
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
        f.write("float main() {\n\n")
        f.write(f"{code_main[0]}\n\n")
        f.write(f"return {code_main[1]};\n")
        f.write("}\n")


write_c_code_to_file(ast, "out.c")
