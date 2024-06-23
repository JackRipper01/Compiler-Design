from typing import Self
import math
import random

import ply
import ply.lex as lex

from lexer import HulkLexer
from lexer import tokens

# constants
PI = math.pi
E = math.e
import hulk_lexer

# Build the lexer
# HL = HulkLexer()
lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0
# lexer = lex.lex() old lexer
###############################################################################################
###############################################################################################

# Parser########################################################################################

import node_classes as nc
import ply.yacc as yacc

# precedence rules for the arithmetic operators
precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "POWER", "POWERSTARSTAR"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "UMINUS"),
)


# region Defining the Grammatical##########################


# region mauricio grammar
def p_empty(p):
    "empty :"
    pass


def p_program(p):
    "program : hl_expression"
    p[0] = p[1]


def p_hl_expression(p):
    """hl_expression : expression SEMI
    | expression_block
    """
    p[0] = p[1]


def p_expression_tbl(p):
    """expression : expression_block"""
    p[0] = p[1]


def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    p[0] = nc.ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]


def p_expression_block_list(p):
    "expression_block_list : hl_expression expression_block_list"
    p[0] = []
    p[0].append(p[1])
    p[0] = p[0] + p[2]


def p_expression_block_list_empty(p):
    """expression_block_list : empty"""
    p[0] = []


def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression"""
    p[0] = nc.Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_let(p):
    """expression : LET assign_values IN expression"""
    p[0] = nc.Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]


def p_assign_values(p):
    """assign_values : NAME EQUAL expression rem_assignments"""
    p[0] = []
    id = nc.ID(p[1])
    assign = nc.Assign(id, p[3])
    id.parent = assign
    p[3].parent = assign
    p[0].append(assign)
    p[0] = p[0] + p[4]


def p_rem_assignments(p):
    "rem_assignments : COMMA NAME EQUAL expression rem_assignments"
    p[0] = []
    id = nc.ID(p[2])
    assign = nc.Assign(id, p[4])
    id.parent = assign
    p[4].parent = assign
    p[0].append(assign)
    p[0] = p[0] + p[5]


def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0] = []


# endregion


# region my grammar
# def p_statement_expr(p):
#     "statement : expression"
#     p[0] = p[1]

# endregion
def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]


def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression POWERSTARSTAR expression
    | expression CONCAT expression"""
    p[0] = nc.BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = nc.UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = nc.Num(p[1])


def p_expression_string(p):
    "expression : STRING"
    p[0] = nc.StringLiteral(p[1])


# constants
def p_expression_pi(p):
    "expression : PI"
    p[0] = nc.Pi()


def p_expression_e(p):
    "expression : E"
    p[0] = nc.E()


# region Built-in functions
def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
    p[0] = nc.Print(p[3])
    p[3].parent = p[0]


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = nc.Sqrt(p[3])
    p[3].parent = p[0]


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = nc.Sin(p[3])
    p[3].parent = p[0]


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = nc.Cos(p[3])
    p[3].parent = p[0]


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = nc.Exp(p[3])
    p[3].parent = p[0]


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = nc.Log(p[3], p[5])
    p[3].parent = p[0]
    p[5].parent = p[0]


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN"
    p[0] = nc.Rand()


# endregion


def p_error(p):
    if p:
        print(f"Syntax error at {p.value}")
    else:
        print("Syntax error at EOF")


# endregion

# region mauricio parser llamacion
# parser = yacc.yacc(start="program")

# hulk_code = """let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
#                             rand();}
#                 {print(rand()-5*3+2);
#                             rand();}
#                             2*23+123;
#                 {let x=2 in let a=7 in print(1+5);
#                  print(let asd=4 in {rand();}); }
#                 {{{print(sin((PI*(((1/2)))+PI)));}}}{{{}}} };"""
# # hulk_code = "print(PI-E);"

# AST = parser.parse(hulk_code)
# endregion
parser = yacc.yacc(start="program")

# Generate AST
hulk_code = """print("Hello World xd" @ "candelisima");"""
ast = parser.parse(hulk_code)

# # semantic and type check
ast.check()

# # evaluate the AST in python code before generating the c code
ast.eval()


import code_generation as cg

# Generate C code
cg.write_c_code_to_file(ast, "out.c")


# ast.graphviz("root")
# # ast.graph.view()
