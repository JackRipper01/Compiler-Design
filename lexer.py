from ply import lex
from ply.lex import TOKEN
import math

import tokenize
OurDecNumber = tokenize.Decnumber + tokenize.maybe(tokenize.Exponent)
OurNumber = tokenize.group(tokenize.Pointfloat, OurDecNumber)

errorList=[]
tokens = []
keywordlist = [
		'print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand', 'function', 'let', 'in', 'if', 'elif', 'else',
		'true', 'false', 'while', 'for', 'range', 'type', 'new', 'inherits', 'is', 'as', 'protocol', 'extends',
		'PI', 'E'
		]

RESERVED = {}
for keyword in keywordlist:
	name = keyword.upper()
	RESERVED[keyword] = name
	tokens.append(name)

tokens = tuple(tokens) + (
		'EQEQUAL','NOTEQUAL','LESSEQUAL', 'GREATEREQUAL',
		'LESS', 'GREATER',

		'COLON','COMMA', 'SEMI',
		'OR','AND',
		
		'EQUAL','DOT',
		
		"NUMBER",
		'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'MOD',

	    'LPAREN', 'RPAREN',
	    'LBRACE', 'RBRACE',
	    'LSQB', 'RSQB',
		'NEWLINE',
		
		'STRING',
		'CONCAT', 'DCONCAT',
		'NAME'
	)

t_EQEQUAL = r'=='
t_NOTEQUAL =  r'!='
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='
t_LESS  = r'<'
t_GREATER = r'>'

t_EQUAL = r'='

t_COLON = r':'
t_COMMA = r','
t_SEMI  = r';'

t_PLUS  = r'\+'
t_MINUS = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_POWER = r'\^'

t_OR  = r'\|'
t_AND = r'&'

t_DOT  = r'\.'

t_DCONCAT = r'@@'
t_CONCAT = r'@'

def t_LPAREN(t):
	r"\("
	t.lexer.parenthesisCount+=1
	return t
def t_RPAREN(t):
	r"\)"
	t.lexer.parenthesisCount-=1
	return t
def t_LBRACE(t):
	r"\{"
	t.lexer.parenthesisCount+=1
	return t
def t_RBRACE(t):
	r"\}"
	t.lexer.parenthesisCount-=1
	return t
def t_LSQB(t):
	r"\["
	t.lexer.parenthesisCount+=1
	return t
def t_RSQB(t):
	r"\]"
	t.lexer.parenthesisCount-=1
	return t

@TOKEN(OurNumber)
def t_NUMBER(t):
    return t

def t_STRING(t):
	r'(\"(\\.|[^\"\n]|(\\\n))*\") | (\'(\\.|[^\'\n]|(\\\n))*\')'
	return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_NAME(t):
	r"[a-zA-Z_][a-zA-Z0-9_]*"
	t.type = RESERVED.get(t.value, "NAME")
	return t

def t_error(t):
    message = "\n# ERROR: Illegal character '%s' in %s at line %d" % (t.value[0], t.value, t.lineno)
    print (message)
    errorList.append(message)
    t.lexer.skip(1)

t_ignore = " \t"

hulk_lexer = lex.lex()
hulk_lexer.parenthesisCount = 0