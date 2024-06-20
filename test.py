import math
import random


PI = math.pi
E = math.e
sin = math.sin
cos = math.cos
log = math.log

#print(sin(2 * PI) * 2 + 3 * PI / log(64, 4))

import lexer


print("\nMIXED TEST\n")
code = """let a = 42, let mod = a % 3 in
    print(
        if (mod == 0) "Magic"
        elif (mod % 3 == 1) "Woke"
        else "Dumb"
    );
"""
lexer.hulk_lexer.input(code)
while True:
	tok = lexer.hulk_lexer.token()
	print(tok)
	if not tok: break

print("\n\nARITHMETIC TEST\n")
code = """print(
	rand()+23.23-1e-12-
    cos(PI+E))"""
lexer.hulk_lexer.input(code)
while True:
	tok = lexer.hulk_lexer.token()
	print(tok)
	if not tok: break

