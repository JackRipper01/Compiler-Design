import base

# Test it out
data = """
3 + 4 * 10
  + -20 *2
"""

# Give the lexer some input
lexer = base.lexer
lexer.input(data)

parser = base.parser
# # Tokenize
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)
# Tokenize other way
# for tok in lexer:
#     print(tok)

print(parser.parse(data, lexer))
