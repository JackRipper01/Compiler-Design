# region old lexer called lex

# List of token names.
tokens = (
    "NUMBER",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIVIDE",
    "LPAREN",
    "RPAREN",
    "PI",
    "E",
    "PRINT",
    "SQRT",
    "SIN",
    "COS",
    "EXP",
    "LOG",
    "RAND",
    "COMMA",
)

# Regular expression rules
t_PLUS = r"\+"
t_MINUS = r"-"
t_TIMES = r"\*"
t_DIVIDE = r"/"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_PI = r"PI"
t_E = r"E"
t_SQRT = r"sqrt"
t_SIN = r"sin"
t_COS = r"cos"
t_EXP = r"exp"
t_LOG = r"log"
t_RAND = r"rand"
t_COMMA = r","
t_PRINT = r"print"

# A string containing ignored characters (spaces and tabs)
t_ignore = " \t"


# A regular expression rule with some action code
def t_NUMBER(t):
    r"\d+"
    t.value = int(t.value)
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# endregion
