import math
import random


PI = math.pi
E = math.e
sin = math.sin
cos = math.cos
log = math.log

#print(sin(2 * PI) * 2 + 3 * PI / log(64, 4))

from lexer import HulkLexer

print("\nTEST I\n")
HL = HulkLexer()
code = """let a = 42, let mod = a % 3 in
    print(
        if (mod == 0) "Magic"
        elif (mod % 3 == 1) "Woke"
        else "Dumb"
    );
"""
HL.input(code)

print("CODE")
print(code)

while True:
	tok = HL.token()
	print(tok)
	if tok.type=='EOFM': break

print("\nTEST II\n")
HL = HulkLexer()
code = """type Person(firstname, lastname) {
    firstname = firstname;
    lastname = lastname;

    name() => self.firstname @@ self.lastname;
}


type Knight inherits Person {
    name() => "Sir" @@ base();
}

let p = new Knight("Phil", "Collins") in
    print(p.name()); // prints 'Sir Phil Collins'
"""
HL.input(code)

print("CODE")
print(code)

while True:
	tok = HL.token()
	print(tok)
	if tok.type=='EOFM': break