import hulk_ast
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc

lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

def p_empty(p):
    'empty :'
    pass

def p_program(p):
	"""program : hl_expression
	"""

def p_hl_expression(p):
	"""hl_expression : expression SEMI
					| expression_block
	"""

def p_expression(p):
	"""expression : expression_block
	"""

def p_expression_block(p):
	"""expression_block : LBRACE expression_block_list RBRACE
	"""

def expression_block_list(p):
	"""expression_block_list : hl_expression expression_block_list
				      | empty
	"""

def p_hl_let(p):
	"""hl_expression : LET assign_values IN hl_expression
	"""

def p_let(p):
	"""expression : LET assign_values IN expression
	"""






