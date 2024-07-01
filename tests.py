import math
import random
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
from typing import Self
import math
import random
import graphviz

do_test_lexer=True
# Testing Lexer
def test_lexer(code):
    lexer = hulk_lexer.lex.lex(module=hulk_lexer)
    lexer.parenthesisCount = 0
    lexer.input(code)

    print("\nCODE")
    print(code)
    while True:
        tok = lexer.token()
        print(tok)
        if not tok: break

if do_test_lexer:
#     test_lexer("""type Person(firstname, lastname) {
#         firstname = firstname;
#         lastname = lastname;

#         name() => self.firstname @@ self.lastname;
#     }


#     type Knight inherits Person {
#         name() => "Sir" @@ base();
#     }

#     let p = new Knight("Phil", "Collins") in
#         print(p.name()); // prints 'Sir Phil Collins'
#     """)

#     test_lexer("""let a = 42, let mod = a % 3 in
#         print(
#             if (mod == 0) "Magic"
#             elif (mod % 3 == 1) "Woke"
#             else "Dumb"
#         );
#     """)

    test_lexer("2+23+3^2**3")
    
    # test_lexer(r"""
    #                function asd:int (a:inr,x:asd) {
    #                 print(a+x)
    #                }
    #                let a = print(sin(10)) in {let a=5, b=6 in {print(rand()-5*3+2);
    #                         rand();}
    #             {print(rand()-5*3+2);
    #                         rand();} 
    #                         2*23+123;
    #             {let x=2 in let a:int=7 in print(1+5);
    #              print(let asd=4 in {rand();}); }
    #             {{{print(sin((PI*(((1/2)))+PI - x)));}}}{{{}}} print('asd'@ "PRINT aaaa \"  "); };""")
    