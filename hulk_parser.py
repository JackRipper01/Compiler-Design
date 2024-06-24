import hulk_lexer
from hulk_lexer import lex, tokens
from ply import yacc
import random
import math
import graphviz

sErrorList=[]

#  BASE NODE AND STRUCTURES

nodes = {}

def add_slf(slf, nm):
    nodes[slf]=nm

class Node:
    
    id = ""
    parent = None

    def __init__(self):
        add_slf(self,"")


    def check(self):
        pass

    def infer_type(self):
        pass

    def eval(self):
        pass
def create_AST_graph(dict: dict, graph_name):
    dot = graphviz.Digraph(graph_name)
    for key in dict.keys():
        if not key.parent:
            dict[key]+=" ( </> )"
        dot.node(str(key), dict[key])
    for key in dict.keys():
        if key.parent:
            dot.edge(str(key.parent), str(key))
    dot.render(directory='output')

# CLASS HIERARCHY

class Program(Node):
    def __init__(self, functions, global_expression):
        add_slf(self, '')
        self.functions = functions
        self.global_exp=global_expression

class FunctionList(Node):
    def __init__(self, functions_list):
        add_slf(self, "FUNCTIONS")
        self.function_list = functions_list

class FunctionDef(Node):
    def __init__(self, func_id, params, body):
        add_slf(self,"FUNC_DEF")
        self.func_id = func_id
        self.params = params
        self.body = body

class FunctionCall(Node):
    def __init__(self, func_id, params):
        add_slf(self,"FUNC_CALL")
        self.func_id = func_id
        self.params = params

class Params(Node):
    def __init__(self, param_list):
        add_slf(self, "params")
        self.param_list = param_list

class ExpressionBlock(Node):
    def __init__(self, exps):
        add_slf(self, 'EXP_BLOCK')
        self.exp_list = exps

class Let(Node):
    def __init__(self,assign, body):
        add_slf(self,'LET')
        self.assign = assign
        self.body = body

class Assign(Node):
    def __init__(self, name, value):
        add_slf(self, 'ASSIGN')
        self.name = name
        self.value = value

class ID(Node):
    def __init__(self, name, opt_type):
        if opt_type == "":
            add_slf(self, "var " + name)
        else: 
            add_slf(self, opt_type+" " + name)

        self.name=name
        self.opt_type = opt_type

#region JTR AST

class BinOp(Node):

    def __init__(self, left, op, right):
        add_slf(self, str(op))
        self.left = left
        self.op = op
        self.right = right

    def __str__(self):
        return f"BinOp({self.op}, {self.left}, {self.right})"

    def check(
        self,
    ):
        self.left.check()
        self.right.check()

        if self.op not in ["+", "-", "*", "/", "^", "**", "@"]:
            raise TypeError(f"Invalid operator: {self.op}")

        left_type = self.left.infer_type()
        right_type = self.right.infer_type()

        if self.op in ["+", "-", "*", "/"]:
            if left_type != "number" or right_type != "number":
                raise TypeError(f"Invalid type for operation: {left_type}")
        if self.op in ["^", "**"]:
            if (
                left_type != "string"
                and left_type != "number"
                or right_type != "number"
                and right_type != "string"
            ):
                raise TypeError(f"Invalid type for operation: {left_type}")


    def infer_type(
        self,
    ):  
        left_type = self.left.infer_type()

        return left_type

    def eval(self):
        if self.op == "+":
            return self.left.eval() + self.right.eval()
        elif self.op == "-":
            return self.left.eval() - self.right.eval()
        elif self.op == "*":
            return self.left.eval() * self.right.eval()
        elif self.op == "/":
            right = self.right.eval()
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return self.left.eval() / right
        elif self.op == "^" or self.op == "**":
            if self.left.eval() < 0 and self.right.eval() != int(self.right.eval()):
                raise ValueError("negative number raised to a non-integer power")
            return self.left.eval() ** self.right.eval()
        elif self.op == "@":
            left_eval = self.left.eval()
            right_eval = self.right.eval()

            return str(left_eval) + str(right_eval)

class UnaryOp(Node):
    def __init__(self, op, operand):
        add_slf(self, str(op))
        self.op = op
        self.operand = operand

    def check(
        self,
    ):  
        self.operand.check()

        if self.op != "-":
            raise TypeError(f"Invalid operator: {self.op}")
        if self.operand.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.operand.infer_type()}")

    def infer_type(self):
        operand_type = self.operand.infer_type()

        return operand_type

    def eval(self):
        if self.op == "-":
            return -self.operand.eval()

class Num(Node):
    def __init__(self, value):
        add_slf(self, str(value))
        if isinstance(value, (int, float)):
            self.value = float(value)
        else:
            self.value = value

    def check(self):
        if not isinstance(self.value, (float)):
            raise TypeError(f"Invalid number: {self.value}")

    def infer_type(self):
        return "number"

    def eval(self):
        return self.value

class StringLiteral(Node):
    def __init__(self, value):
        add_slf(self,value)
        self.value = value
        # print(value)

    def __str__(self):
        return str(self.value)

    def check(self):
        pass

    def infer_type(self):
        return "string"

    def eval(self):
        return self.value

class Pi(Node):
    def __init__(self):
        add_slf(self,'PI')

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return math.pi

class E(Node):
    def __init__(self):
        add_slf(self,'E')

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return math.e

class Print(
    Node
):  
    def __init__(self, value):
        add_slf(self, "PRINT")
        self.value = value

    def check(self):
        self.value.check()

    def infer_type(self):
        return "void"

    def eval(self):
        print(self.value.eval())

class Sqrt(Node):
    def __init__(self, value):
        add_slf(self,"SQRT")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")
        if self.value.eval() < 0:
            raise ValueError("sqrt of a negative number")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sqrt(self.value.eval())

class Sin(Node):
    def __init__(self, value):
        add_slf(self, "SIN")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.sin(self.value.eval())

class Cos(Node):
    def __init__(self, value):
        add_slf(self, "COS")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.cos(self.value.eval())

class Exp(Node):
    def __init__(self, value):
        add_slf(self,"EXP")
        self.value = value

    def check(self):
        self.value.check()
        if self.value.infer_type() != "number":
            raise TypeError(f"Invalid type for operation: {self.value.infer_type()}")

    def infer_type(self):
        return "number"

    def eval(self):
        return math.exp(self.value.eval())

class Log(Node):
    def __init__(self, value, base):
        add_slf(self,"LOG")
        self.base = base
        self.value = value

    def check(self):
        self.base.check()
        self.value.check()
        if self.base.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in base of log: {self.base.infer_type()}"
            )
        if self.value.infer_type() != "number":
            raise TypeError(
                f"Invalid type for operation in argument of log: {self.value.infer_type()}"
            )

    def infer_type(self):
        return "number"

    def eval(self):
        return math.log(self.base.eval(), self.value.eval())

class Rand(Node):
    def __init__(self):
        add_slf(self,"RAND")

    def check(self):
        pass

    def infer_type(self):
        return "number"

    def eval(self):
        return random.uniform(0, 1)

#endregion

#region GRAMMAR

lexer = hulk_lexer.lex.lex(module=hulk_lexer)
lexer.parenthesisCount = 0

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "TIMES", "DIVIDE"),
    ("right", "POWER"),
    ("right", "LPAREN", "RPAREN"),
    ("nonassoc", "UMINUS"),
)

def p_empty(p):
    'empty :'
    pass

def p_opt_type(p):
    "opt_type : COLON NAME"
    p[0] = p[2]


def p_opt_type_e(p):
    "opt_type : empty"
    p[0] = ""

def p_namedef(p):
    "namedef : NAME opt_type"
    p[0] = ID(p[1], p[2])

def p_program(p):
    "program : functions hl_expression"
    p[0] = Program(p[1],p[2])
    p[2].parent = p[0]
    for i in p[1]:
        i.parent = p[0]
        
def p_function_list_items(p):
    "functions : function_def functions"
    p[0] = [p[1]]+p[2]

def p_function_list_items_empty(p):
    "functions : empty"
    p[0]=[]

def p_exp_func_call(p):
    "expression : func_call"
    p[0]=p[1]

def p_func_call(p):
    "func_call : NAME LPAREN cs_exps RPAREN"
    id = ID(p[1],"")
    p[0] = FunctionCall(id,p[3])
    id.parent = p[0]
    p[3].parent = p[0]


def p_cs_exps(p):
    "cs_exps : cs_exps_list"
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]

def p_cs_exps_list(p):
    "cs_exps_list : expression cs_exps_list_rem"
    p[0] = [p[1]]+p[2]

def p_cs_exps_list_e(p):
    "cs_exps_list : empty"
    p[0] = []

def p_cs_exps_list_rem(p):
    "cs_exps_list_rem : COMMA expression cs_exps_list_rem"
    p[0] = [p[2]]+p[3]

def p_cs_exps_list_rem_e(p):
    "cs_exps_list_rem : empty"
    p[0] = []

def p_function_def(p):
    "function_def : FUNCTION namedef LPAREN func_params RPAREN INLINE hl_expression"
    p[0] = FunctionDef(p[2],p[4],p[7])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[7].parent = p[0]

def p_function_def_fullform(p):
    "function_def : FUNCTION namedef LPAREN func_params RPAREN expression_block"
    p[0] = FunctionDef(p[2],p[4],p[6])
    p[2].parent = p[0]
    p[4].parent = p[0]
    p[6].parent = p[0]

def p_func_params(p):
    "func_params : func_params_list"
    p[0] = Params(p[1])
    for i in p[1]:
        i.parent = p[0]

def p_func_params_list(p):
    "func_params_list : namedef func_params_list_rem"
    p[0] = [p[1]]+p[2]

def p_func_params_list_e(p):
    "func_params_list : empty"
    p[0] = []

def p_func_params_list_rem(p):
    "func_params_list_rem : COMMA namedef func_params_list_rem"
    p[0] = [p[2]]+p[3]

def p_func_params_list_rem_e(p):
    "func_params_list_rem : empty"
    p[0] = []

def p_hl_expression(p):
    """hl_expression : expression SEMI
					| expression_block
	"""
    p[0] = p[1]

def p_expression_tbl(p):
    """expression : expression_block
	"""
    p[0]=p[1]

def p_expression_block(p):
    "expression_block : LBRACE expression_block_list RBRACE"
    p[0] = ExpressionBlock(p[2])
    for i in p[2]:
        i.parent = p[0]

def p_expression_block_list(p):
    "expression_block_list : hl_expression expression_block_list"
    p[0]=[p[1]]+p[2]

def p_expression_block_list_empty(p):
    """expression_block_list : empty
	"""
    p[0]=[]

def p_hl_let(p):
    """hl_expression : LET assign_values IN hl_expression
	"""
    p[0]=Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]

def p_let(p):
    """expression : LET assign_values IN expression
	"""
    p[0]=Let(p[2], p[4])
    for i in p[2]:
        i.parent = p[0]
    p[4].parent = p[0]

def p_assign_values(p):
    """assign_values : namedef EQUAL expression rem_assignments
	"""
    assign = Assign(p[1], p[3])
    p[1].parent=assign
    p[3].parent = assign
    p[0] = [assign]+p[4]

def p_rem_assignments(p):
    "rem_assignments : COMMA namedef EQUAL expression rem_assignments"

    assign = Assign(p[2], p[4])
    p[2].parent=assign
    p[4].parent = assign
    p[0]= [assign] + p[5]

def p_rem_assignments_empty(p):
    "rem_assignments : empty"
    p[0]=[]

def p_expression_group(p):
    "expression : LPAREN expression RPAREN"
    p[0] = p[2]

def p_expression_binop(p):
    """expression : expression PLUS expression
    | expression MINUS expression
    | expression TIMES expression
    | expression DIVIDE expression
    | expression POWER expression
    | expression CONCAT expression
    | expression DCONCAT expression"""
    p[0] = BinOp(left=p[1], op=p[2], right=p[3])
    p[1].parent = p[0]
    p[3].parent = p[0]


def p_expression_uminus(p):
    "expression : MINUS expression %prec UMINUS"  # no se que significa el %prec UMINUS ese,recomiendo ignorarlo hasta q se parta algo
    p[0] = UnaryOp(op=p[1], operand=p[2])
    p[2].parent = p[0]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = Num(p[1])

def p_expression_string(p):
    "expression : STRING"
    p[0] = StringLiteral(p[1])

def p_expression_variable(p):
    "expression : NAME"
    p[0] = ID(p[1],"")

def p_expression_pi(p):
    "expression : PI"
    p[0] = Pi()


def p_expression_e(p):
    "expression : E"
    p[0] = E()


def p_expression_print(p):
    "expression : PRINT LPAREN expression RPAREN"
    p[0] = Print(p[3])
    p[3].parent = p[0]

def p_expression_sqrt(p):
    "expression : SQRT LPAREN expression RPAREN"
    p[0] = Sqrt(p[3])
    p[3].parent = p[0]


def p_expression_sin(p):
    "expression : SIN LPAREN expression RPAREN"
    p[0] = Sin(p[3])
    p[3].parent = p[0]



def p_expression_cos(p):
    "expression : COS LPAREN expression RPAREN"
    p[0] = Cos(p[3])
    p[3].parent = p[0]


def p_expression_exp(p):
    "expression : EXP LPAREN expression RPAREN"
    p[0] = Exp(p[3])
    p[3].parent = p[0]


def p_expression_log(p):
    "expression : LOG LPAREN expression COMMA expression RPAREN"
    p[0] = Log(p[3], p[5])
    p[3].parent = p[0]
    p[5].parent = p[0]


def p_expression_rand(p):
    "expression : RAND LPAREN RPAREN"
    p[0] = Rand()


def p_error(p):
    if p:
        sErrorList.append(f"Syntax error at {p.value} near line: {p.lineno -1}")
    else:
        sErrorList.append("Syntax error at EOF")
    print(sErrorList[-1])

#endregion

#region Generate AST
parser = yacc.yacc(start="program")

# add r prefix so it takes the line escape, not necessary to add any step when reading a file

ex_code = r"""
                   function asd (a,x) {
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
                            rand();}
                {print(rand()-5*3+2);
                            rand();} 
                            2*23+123;
                {let x=2 in let a:int=7 in print(1+5);
                 print(let asd=4 in {rand();}); AAAAAAA();}
                {{{print(sin((PI*(((1/2)))+PI * x + f() - asd(x,y) )));}}}{{{}}} print('asd'@ "PRINT aaaa \"  "); };"""

AST = parser.parse(
r"""function a(b,c) => print(b+c);
function siuuu: number (x,y,z) {print(x);print(y);print(z);}
{
    let a = 1 in let b: number = a+3 in print (siuuu(a+b,a,a(b,a)));
    print("asdasd");
}
"""
)

if len(sErrorList)==0:
    create_AST_graph(nodes, "AST")
else:
    print("\nPARSING FINISHED WITH ERRORS:")
    for i in sErrorList:
        print(" - ", i)

#endregion
#xd