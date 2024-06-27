from ply import lex
from ply.lex import TOKEN
import tokenize

OurDecNumber = tokenize.Decnumber + tokenize.maybe(tokenize.Exponent)
OurNumber = tokenize.group(tokenize.Pointfloat, OurDecNumber)
OurString = tokenize.group(r"'[^\n'\\]*(?:\\.[^\n'\\]*)*'",
               r'"[^\n"\\]*(?:\\.[^\n"\\]*)*"')
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
		'NOT', 'OR','AND',
		
		'EQUAL', 'ASSDESTROYER', 'DOT', 'INLINE',
		
		"NUMBER",
		'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'POWER', 'MOD',

	    'LPAREN', 'RPAREN',
	    'LBRACE', 'RBRACE',
	    'LSQB', 'RSQB',
		'NEWLINE',
		
		'STRING',
		'CONCAT', 'DCONCAT',
		'NAME', 
		
		'EOFM'
	)

t_EQEQUAL = r'=='
t_NOTEQUAL =  r'!='
t_LESSEQUAL = r'<='
t_GREATEREQUAL = r'>='
t_LESS  = r'<'
t_GREATER = r'>'

t_INLINE = r'=>'
t_EQUAL = r'='
t_ASSDESTROYER = r':='

t_COLON = r':'
t_COMMA = r','
t_SEMI  = r';'

t_PLUS  = r'\+'
t_MINUS = r'-'
t_TIMES  = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_POWER = r'\^|\*\*'

t_OR  = r'\|'
t_AND = r'&'
t_NOT = r'!'

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

def t_comment(t):
	r"[ ]*//[^\n]*"
	pass

@TOKEN(OurNumber)
def t_NUMBER(t):
    return t

@TOKEN(OurString)
def t_STRING(t):
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

if __name__=="__main__":
	lexer = lex.lex()
	lexer.parenthesisCount = 0
	toks = lexer.input(r"""{function asd (a,x) {
                    print(a+x);
                   }
                   function asd (a,x) => {
                    print(a+x);
                   }
                   function asd (a,x) => {
                    print(a+x);
                   };
                   function asdf (a,x) => print(a+x);
                   let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
                            rand();};
                {print(rand()-5*3+2);
                            rand();} ;
                            2*23+123;
                {let x=2 in let a:int=7 in print(1+5);
                 print(let asd=4 in {rand();}); AAAAAAA();}
                {{{print(sin((PI*(((1/2)))+PI * x + f() - asd(x,y) )));}}}{{{}}} print('asd'@ "PRINT aaaa \"  "); };}""")
	for i in lexer:
		print(i)