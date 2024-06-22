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

# Build the lexer
HL = HulkLexer()

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
def p_statement_expr(p):
    "statement : expression"
    p[0] = p[1]


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


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = nc.UnaryOp(op=p[1], operand=p[2])


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


def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = nc.Sqrt(p[3])


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = nc.Sin(p[3])


def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = nc.Cos(p[3])


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = nc.Exp(p[3])


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = nc.Log(p[3], p[5])


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


parser = yacc.yacc()

# Generate AST
hulk_code = "print('Hello World!' @ 'candela')"
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
