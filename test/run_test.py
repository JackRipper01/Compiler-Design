from hulk_semantic_check import semantic_check
from hulk_lexer import errorList as lexerErrors
from hulk_parser import hulk_parse
from misc import create_AST_graph, get_descendancy_set, typeof, ColumnFinder
from hulk_code_gen import CodeGen
from hulk_ast import nodes

def code_gen_test():
    code = """type Person(firstname:String, lastname:String) {
    firstname = firstname;
    lastname = lastname;

    name():String => self.firstname @@ self.lastname;
}

type Knight inherits Person {
    name():String => "Sir" @@ "base()";
}

let p = new Knight("Phil", "Collins") in print(p.name());
"""
    cf = ColumnFinder()
    
    ast, parsingErrors, _b = hulk_parse(
        code, cf)
    print(code)
    create_AST_graph(nodes, "AST")

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
