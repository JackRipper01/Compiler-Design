from misc import refact_ast, create_AST_graph, find_column, StringToken

import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
import hulk_ast
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

lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

sErrorList = []

precedence = (
    # ("right", "PRINT","SQRT","SIN","COS","EXP","LOG","RAND"),
    ("right", "LET", "IN"),
    ("right", "IF", "ELIF", "ELSE"),
    ("right", "WHILE", "FOR"),
    ("nonassoc", "EQUAL"),
    ("right", "ASSDESTROYER"),
    ("left", "AS"),
    ("left", "IS"),
    ("left", "CONCAT", "DCONCAT"),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "EQEQUAL", "NOTEQUAL"),
    ("nonassoc", "LESSEQUAL", "GREATEREQUAL", "LESS", "GREATER"),
    ("right", "NOT"),
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE", "MOD"),
    ("right", "POWER"),
    ("right", "UMINUS"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "NAME"),
    ("left", "DOT"),
)


def p_empty(p):
    "empty :" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    pass


def p_opt_type(p):
    "opt_type : COLON NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[2]


def p_opt_type_e(p):
    "opt_type : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = "" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
def p_namedef(p):
    "namedef : NAME opt_type" #tag_replace
    if type(p) is yacc.YaccProduction:
        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[1], p[2])


def p_program(p):
    "program : functions_types_protocols global_hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Program(p[1], p[2])
    for i in p[1]:
        i.parent = p[0]
    if p[2]:
        p[2].parent = p[0]


def p_global_hl_expression(p):
    "global_hl_expression : hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_global_hl_expression_e(p):
    "global_hl_expression : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = None


def p_functionsx_types_protocols_list_items(p):
    "functions_types_protocols : function_def functions_types_protocols" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_functions_typesx_protocols_list_items(p):
    "functions_types_protocols : type_def functions_types_protocols" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_functions_types_protocolsx_list_items(p):
    "functions_types_protocols : protocol_def functions_types_protocols" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_function_type_list_items_empty(p):
    "functions_types_protocols : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_protocol(p):
    "protocol_def : PROTOCOL NAME opt_extends LBRACE protocol_methods RBRACE opt_semi" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[2], "")
    p[0] = Protocol(id, p[5], p[3])
    id.parent = p[0]
    for i in p[5]:
        i.parent = p[0]
    if p[3]:
        p[3].parent = p[0]


def p_protocol_extends(p):
    "opt_extends : EXTENDS NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[2], "")


def p_protocol_extends_e(p):
    "opt_extends : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = None


def p_protocol_methods(p):
    "protocol_methods : protocol_method protocol_methods" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_protocol_methods_e(p):
    "protocol_methods : protocol_method empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]]


def p_protocol_method(p):
    "protocol_method : NAME LPAREN protocol_method_params RPAREN COLON NAME SEMI" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[1], p[6])
    params = Params(p[3])
    for i in p[3]:
        i.parent = params
    p[0] = FunctionDef(id, params, None)
    id.parent = p[0]
    params.parent = p[0]


def p_protocol_method_params(p):
    "protocol_method_params : NAME COLON NAME protocol_method_params_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [ID(p[1], p[3])] + p[4]


def p_protocol_method_params_e(p):
    "protocol_method_params : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_protocol_method_params_rem(p):
    "protocol_method_params_rem : COMMA NAME COLON NAME protocol_method_params_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [ID(p[2], p[4])] + p[5]


def p_protocol_method_params_rem_e(p):
    "protocol_method_params_rem : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_exp_func_call(p):
    "expression : func_call_next" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_func_call(p):
    "func_call_next : NAME LPAREN cs_exps RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[1], "")
    p[0] = FunctionCall(id, p[3])
    id.parent = p[0]
    p[3].parent = p[0]


# endregion
# endregion
def p_exp_type_call(p):
    "expression : type_call" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_type_call(p):
    "type_call : NEW NAME LPAREN cs_exps RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[2], p[2])
    p[0] = TypeCall(id, p[4])
    id.parent = p[0]
    p[4].parent = p[0]


def p_cs_exps(p):
    "cs_exps : cs_exps_list" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]


def p_cs_exps_list(p):
    "cs_exps_list : expression cs_exps_list_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_cs_exps_list_e(p):
    "cs_exps_list : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_cs_exps_list_rem(p):
    "cs_exps_list_rem : COMMA expression cs_exps_list_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[2]] + p[3]


def p_cs_exps_list_rem_e(p):
    "cs_exps_list_rem : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_function_def(p):
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type INLINE hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[2], p[6])
    p[0] = FunctionDef(id, p[4], p[8])
    id.parent = p[0]
    p[4].parent = p[0]
    p[8].parent = p[0]


def p_function_def_fullform(p):
    "function_def : FUNCTION NAME LPAREN func_params RPAREN opt_type expression_block opt_semi" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[2], p[6])
    p[0] = FunctionDef(id, p[4], p[7])
    id.parent = p[0]
    p[4].parent = p[0]
    p[7].parent = p[0]


def p_func_params(p):
    "func_params : func_params_list" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]


def p_func_params_list(p):
    "func_params_list : namedef func_params_list_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_func_params_list_e(p):
    "func_params_list : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_func_params_list_rem(p):
    "func_params_list_rem : COMMA namedef func_params_list_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[2]] + p[3]


def p_func_params_list_rem_e(p):
    "func_params_list_rem : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_type_def(p):
    "type_def : TYPE NAME opt_type_params opt_inheritance LBRACE type_members RBRACE opt_semi" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    params = Params(p[3])
    for i in p[3]:
        i.parent = params
    id = ID(p[2], p[2])

    p[0] = TypeDef(id, params, p[6], p[4])
    for i in p[6]:
        i.parent = p[0]
    params.parent = p[0]
    id.parent = p[0]
    if p[4]:
        p[4].parent = p[0]


def p_opt_inheritance(p):
    "opt_inheritance : INHERITS NAME opt_inheritance_params" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[2], "")
    p[0] = TypeCall(id, p[3])
    p[3].parent = p[0]
    id.parent = p[0]


def p_opt_inheritance_e(p):
    "opt_inheritance : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = None


def p_opt_inheritance_params(p):
    "opt_inheritance_params : LPAREN cs_exps RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[2]


def p_opt_inheritance_params_e(p):
    "opt_inheritance_params : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Params([])


def p_opt_type_params(p):
    "opt_type_params : LPAREN typedef_params RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[2]


def p_opt_type_params_e(p):
    "opt_type_params : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_typedef_params(p):
    "typedef_params : namedef typedef_params_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_typedef_params_e(p):
    "typedef_params : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_typedef_params_rem(p):
    "typedef_params_rem : COMMA namedef typedef_params_rem" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[2]] + p[3]


def p_typedef_params_rem_e(p):
    "typedef_params_rem : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_type_members(p):
    "type_members : type_member type_members" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_type_members_e(p):
    "type_members : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_member_func(p):
    "type_member : member_func" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_member_function_def(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type INLINE hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[1], p[5])
    p[0] = FunctionDef(id, p[3], p[7])
    id.parent = p[0]
    p[3].parent = p[0]
    p[7].parent = p[0]


def p_member_function_def_fullform(p):
    "member_func : NAME LPAREN func_params RPAREN opt_type expression_block opt_semi" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    id = ID(p[1], p[5])
    p[0] = FunctionDef(id, p[3], p[6])
    id.parent = p[0]
    p[3].parent = p[0]
    p[6].parent = p[0]


def p_member_var(p):
    "type_member : member_var" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_member_var_dec(p):
    "member_var : namedef EQUAL hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Assign(p[1], p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


# region temporal
def p_expression_tbl(p):
    """expression : expression_block""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_hl_expression(p):
    """hl_expression : expression SEMI
    | expression_block
    """ #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]


def p_expression_block_list(p):
    "expression_block_list : hl_expression expression_block_list" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = [p[1]] + p[2]


def p_expression_block_list_e(p):
    "expression_block_list : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_let(p):
    """expression : LET assign_values IN expression""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_assign_values(p):
    """assign_values : namedef EQUAL expression rem_assignments""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    assign = Assign(p[1], p[3])
    p[1].parent = assign
    p[3].parent = assign
    p[0] = [assign] + p[4]


def p_rem_assignments(p):
    "rem_assignments : COMMA namedef EQUAL expression rem_assignments" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    assign = Assign(p[2], p[4])
    p[2].parent = assign
    p[4].parent = assign
    p[0] = [assign] + p[5]


def p_rem_assignments_empty(p):
    "rem_assignments : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


# endregion
def p_if_hl(p):
    "hl_expression : IF expression_parenthized expression opt_elifs ELSE hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].case_list:
        i.parent = p[0]


# region temporal


def p_if_exp(p):
    "expression : IF expression_parenthized expression opt_elifs ELSE expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    first = Case(p[2], p[3], "if")
    p[2].parent = first
    p[3].parent = first

    else_cond = TrueLiteral()
    last = Case(else_cond, p[6], "else")
    else_cond.parent = last
    p[6].parent = last

    p[0] = If([first] + p[4] + [last])

    for i in p[0].case_list:
        i.parent = p[0]


def p_opt_elifs(p):
    "opt_elifs : ELIF expression_parenthized expression opt_elifs" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    elif_cond = Case(p[2], p[3], "elif")
    p[2].parent = elif_cond
    p[3].parent = elif_cond
    p[0] = [elif_cond] + p[4]


def p_opt_elifs_e(p):
    "opt_elifs : empty" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = []


def p_opt_semi(p):
    """opt_semi : SEMI
    | empty""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
def p_for_hl(p):
    "hl_expression : FOR LPAREN destroyable IN expression RPAREN hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    for_exp = For(p[3], p[5], p[7])
    p[3].parent = for_exp
    p[5].parent = for_exp
    p[7].parent = for_exp
    p[0] = Let([], for_exp)
    for_exp.parent = p[0]


def p_for(p):
    "expression : FOR LPAREN destroyable IN expression RPAREN expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    for_exp = For(p[3], p[5], p[7])
    p[3].parent = for_exp
    p[5].parent = for_exp
    p[7].parent = for_exp
    p[0] = Let([], for_exp)
    for_exp.parent = p[0]


def p_while_hl(p):
    "hl_expression : WHILE expression_parenthized hl_expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = While(p[2], p[3])
    p[2].parent = p[0]
    p[3].parent = p[0]


def p_while(p):
    "expression : WHILE expression_parenthized expression" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = While(p[2], p[3])
    p[2].parent = p[0]
    p[3].parent = p[0]


def p_expression_group(p):
    "expression : expression_parenthized" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_expression_parenthized(p):
    "expression_parenthized : LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[2]


def p_expression_binop(p:yacc.YaccProduction):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression MOD expression
    | expression CONCAT expression
    | expression DCONCAT expression
    | expression AND expression
    | expression OR expression
    | expression EQEQUAL expression
    | expression NOTEQUAL expression
    | expression LESSEQUAL expression
    | expression GREATEREQUAL expression
    | expression LESS expression
    | expression GREATER expression
    | destroyable ASSDESTROYER expression
    | member_resolute ASSDESTROYER expression
    | expression IS type_test
    | expression AS type_test
    """ #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    if p[2] == ":=":
        p[0] = BinOp(left=p[1], op="AD", right=p[3])
    else:
        p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_binop_hl(p):
    """hl_expression : expression PLUS hl_expression
    | expression MINUS hl_expression
    | expression TIMES hl_expression
    | expression DIVIDE hl_expression
    | expression POWER hl_expression
    | expression MOD hl_expression
    | expression CONCAT hl_expression
    | expression DCONCAT hl_expression
    | expression AND hl_expression
    | expression OR hl_expression
    | expression EQEQUAL hl_expression
    | expression NOTEQUAL hl_expression
    | expression LESSEQUAL hl_expression
    | expression GREATEREQUAL hl_expression
    | expression LESS hl_expression
    | expression GREATER hl_expression
    | destroyable ASSDESTROYER hl_expression
    | member_resolute ASSDESTROYER hl_expression
    """ #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    if p[2] == ":=":
        p[0] = BinOp(left=p[1], op="AD", right=p[3])
    else:
        p[0] = BinOp(left=p[1], op=p[2], right=p[3])

    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_destroyable(p):
    "destroyable : NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[1], "")


def p_type_test(p):
    "type_test : NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[1], p[1])


def p_exp_member_resolute(p):
    "expression : member_resolute" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_member_resolute(p):
    "member_resolute : expression DOT member_resolut" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_member_resolut_fc(p):
    "member_resolut : func_call_next" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_member_resolut_att(p):
    "member_resolut : NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[1], "")


def p_expression_unary(p):
    """expression : NOT expression
    | MINUS expression %prec UMINUS""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_unary_hl(p):
    """hl_expression : NOT hl_expression
    | MINUS hl_expression %prec UMINUS""" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Num(p[1])


def p_expression_string(p):
    "expression : STRING" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = StringLiteral(p[1])


def p_expression_variable(p):
    "expression : NAME" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = ID(p[1], "")


def p_expression_vector(p):
    "expression : vector" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = p[1]


def p_vector_ext(p):
    "vector : LSQB cs_exps RSQB" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = VectorExt(p[2])
    p[2].parent = p[0]


def p_vector_int(p):
    "vector : LSQB expression SUCH_AS destroyable IN expression RSQB" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = VectorInt(p[2], p[4], p[6])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[6].parent = p[0]


def p_expression_vector_ind_pare(p):
    "expression :  expression LSQB expression RSQB" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = VectorCall(p[1], p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_pi(p):
    "expression : PI" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Pi()


def p_expression_e(p):
    "expression : E" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = E()


def p_expression_true(p):
    "expression : TRUE" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = TrueLiteral()


def p_expression_false(p):
    "expression : FALSE" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = FalseLiteral()


def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Print(p[3])
    p[3].parent = p[0]


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Sqrt(p[3])
    p[3].parent = p[0]


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Sin(p[3])
    p[3].parent = p[0]


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Cos(p[3])
    p[3].parent = p[0]


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Exp(p[3])
    p[3].parent = p[0]


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Log(p[3], p[5])
    p[3].parent = p[0]
    p[5].parent = p[0]


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN" #tag_replace
    if type(p) is yacc.YaccProduction:

        for i in range(len(p)):
            if type(p[i]) is str:
                p[i] = StringToken(p[i])
                p[i].lineno = p.lineno(i)
                p[i].lexpos = p.lexpos(i)
    p[0] = Rand()


def p_error(p):
    sErrorList.append(p)
    # print(sErrorList[-1])


def hulk_parse(code, cf = None, create_graph = False, nm = "AST"):
    "parsea el codigo de hulk, retornando la raiz del ast"
    nodes = hulk_ast.nodes
    
    parser = yacc.yacc(start="program", method="LALR")

    AST = parser.parse(code)
    
    errors = []
    if len(sErrorList) == 0:
        nodes = refact_ast(nodes)
        if create_graph:
            create_AST_graph(nodes, nm)
        AST.input = code
        if cf:
            cf.code = code
        return AST, sErrorList, nodes
    else:
        for i in sErrorList:
            if i:
                errors.append(f"Syntax error near '{i.value}' at line {i.lineno}, column {find_column(code,i)}")
            else:
                errors.append("Syntax error at EOF")
            # break

        return None, errors, None
