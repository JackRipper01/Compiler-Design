import math
import random
import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
from typing import Self
import math
import random
import graphviz
from hulk_parser import hulk_parse
from type_checking import Type_Check
import hulk_ast
from misc import flip_dict

# Parsing and creating AST
tests=[
    #0
    '42;',
    #1
    'print(42);',
    #2
    'print((((1 + 2) ^ 3) * 4) / 5);',
    #3
    'print("The meaning of life is " @ 42);',
    #4
    'print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));',
    #5
    '''{
    print(42);
    print(sin(PI/2));
    print("Hello World");
    }''',
    #6
    '''function tan(x) => sin(x) / cos(x);''',
    #7
    '''
    function cot(x) => 1 / tan(x);
    function tan(x) => sin(x) / cos(x);
    print(tan(PI) ** 2 + cot(PI) ** 2);
    ''',
    #8
    '''
    function operate(x, y) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
    }   
    print("Hola Mundo");
    ''',
    #9
    '''
    function operate(x, y) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
    }   
    operate(4,2);
    operate(2,3);
    ''',
    ]

def run_single_test(index):
    ast,nodes=hulk_parse(tests[index],True)
    nodes = flip_dict(nodes)
    # for e in nodes.keys():
    #     print(f'{e}: {nodes[e]}')
    # print(nodes[''])
    # t= Type_Check(nodes[''])
    Type_Check.check_type(nodes[''],test_mode=True)

run_single_test(8)

# Testing Lexer
do_test_lexer=False
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
    