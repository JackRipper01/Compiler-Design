# region temp import 
from hulk_parser import hulk_parse
from hulk_ast import nodes
from misc import create_AST_graph, refact_ast
# endregion

import visitor

from hulk_ast import (
    Node,
    Program,
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
)

class ScopeBuilder:
    def __init__(self):
        self.errors = []

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node):
        node.a = "bu ja ja"

    def get_global_definitions(self, ast_input : Program):
        for function in ast_input.functions:
            function_name = function.func_id.name+"/"+str(len(function.params.param_list))
            if function_name in ast_input.global_definitions:
                print("Duplicated function: "+ function_name)
                self.errors.append("Duplicated function: "+ function_name)
            else:
                ast_input.global_definitions[function_name] = function
        
        for type_def in ast_input.types:
            type_name = type_def.id.name
            if type_name in ast_input.global_definitions:
                self.errors.append("Duplicated type: "+ type_name)
            else:
                ast_input.global_definitions[type_name] = type_def
        
        for protocol in ast_input.protocols:
            protocol_name = protocol.id.name
            if protocol_name in ast_input.global_definitions:
                self.errors.append("Duplicated type: "+ protocol_name)
            else:
                ast_input.global_definitions[protocol_name] = protocol
    
        print(ast_input.global_definitions)

def semantic_check(ast: Program):
    SB = ScopeBuilder()
    SB.get_global_definitions(ast)
    # your code here

if __name__ == "__main__":
    ast = hulk_parse(r"function asd(a,v, wer) => print(x);function asd(a,v, wer) => print(x);type Point {}protocol Point{doo():xd;}")
    nodes = refact_ast(nodes)
    create_AST_graph(nodes, "AST")
    ScopeBuilder().get_global_definitions(ast)