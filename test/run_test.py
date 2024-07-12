import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from hulk_semantic_check import semantic_check
from hulk_lexer import errorList as lexerErrors
from hulk_parser import hulk_parse
from misc import create_AST_graph, get_descendancy_set, typeof, ColumnFinder
from hulk_code_gen import CodeGen
from hulk_ast import nodes

try:
    os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz/bin/'
except:
    pass

def run_test(filename):
    file= open(filename,'r')
    code= file.read()
    file.close()
    cf = ColumnFinder()
    
    ast, parsingErrors, _b = hulk_parse(
        code, cf)
    print(code)
    #create_AST_graph(nodes, "AST")

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
        ast, semantic_check_errors = semantic_check(ast, cf)

        print(
            (
                "SEMANTIC CHECK FOUND THE FOLLOWING ERRORS:"
                if len(semantic_check_errors) > 0
                else "SEMANTIC CHECK OK!!!"
            ),
            *semantic_check_errors,
            sep="\n - ",
        )
        print("\nGlobal Expression returned:", typeof(ast.global_exp))
        if len(semantic_check_errors) == 0:
            pass
        CodeGen().visit(ast)

# run_test('./test/custom_test.hulk')
# run_test('./test/numbers_test.hulk')
# run_test('./test/for_test.hulk')
# run_test('./test/function_test.hulk')
run_test('./test/test.hulk')