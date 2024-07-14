from hulk_lexer import errorList as lexerErrors
from hulk_parser import hulk_parse
from hulk_semantic_check import semantic_check
from hulk_code_gen import CodeGen

from misc import typeof
import io

CODE = io.open("test.hulk").read()
snippet = """
protocol Iterable {
    next() : Boolean;
    current() : Object;
}
let numbers = [1,2,3,4,5,6,7,8,9] in
        for (x in numbers)
            print(x);"""
ast, parsingErrors, nodes = hulk_parse(
        CODE, create_graph=True)

print(
    "LEXER FOUND THE FOLLOWING ERRORS:" if len(
        lexerErrors) > 0 else "LEXING OK!",
    *lexerErrors,
    sep="\n - ",
)
print(
    (
        "PARSER FOUND THE FOLLOWING ERRORS:"
        if len(parsingErrors) > 0
        else "PARSING OK!!"
    ),
    *parsingErrors,
    sep="\n - ",
)
if ast:
    ast, semantic_check_errors = semantic_check(ast, CODE)

    print(
        (
            "SEMANTIC CHECK FOUND THE FOLLOWING ERRORS:"
            if len(semantic_check_errors) > 0
            else "SEMANTIC CHECK OK!!!"
        ),
        *semantic_check_errors,
        sep="\n - ",
    )
    if len(semantic_check_errors) == 0:
        print("\nGlobal Expression returned:", typeof(ast.global_exp))
        CodeGen().visit(ast)