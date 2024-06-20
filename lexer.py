from ply import lex

tokens = []

keywordlist = [
		'print', 'sqrt', 'sin', 'cos', 'exp', 'log', 'rand', 'function', 'let', 'in', 'if', 'elif', 'else',
		'true', 'false', 'while', 'for', 'range', 'type', 'new', 'inherits', 'is', 'as', 'protocol', 'extends'
		]

RESERVED = {}
for keyword in keywordlist:
	name = keyword.upper()
	RESERVED[keyword] = name
	tokens.append(name)
