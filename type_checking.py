
# region Type Checking
from hulk_semantic_check import ScopeBuilder
from hulk_ast import *

class Type_Check():
    
    def __innit__(self,ast:Program):
        self.context= ScopeBuilder.get_global_definitions(ast)
        
    @classmethod
    def check_type(cls,node: Node, infered_type=[],test_mode=False):
        t=''
        if isinstance(node,Assign):
            t= cls.assign_check_type(node)
        elif isinstance(node, Num):
            t= cls.number_check_type(node)
        elif isinstance(node, StringLiteral):
            t= cls.string_check_type(node)
        elif isinstance(node, Let):
            t= cls.let_check_type(node)
        elif isinstance(node, Print):
            t= cls.print_check_type(node)
        elif isinstance(node, BinOp):
            t= cls.binop_check_type(node)
        elif isinstance(node, Exp):
            t= cls.exp_check_type(node)
        elif isinstance(node, Log):
            t= cls.log_check_type(node)
        elif isinstance(node, Cos):
            t= cls.cos_check_type(node)
        elif isinstance(node, Rand):
            t= cls.rand_check_type(node)
        elif isinstance(node, Pi):
            t= cls.pi_check_type(node)
        elif isinstance(node, E):
            t= cls.e_check_type(node)
        elif isinstance(node, Sin):
            t= cls.sin_check_type(node)
        elif isinstance(node, Sqrt):
            t= cls.sqrt_check_type(node)
        elif isinstance(node, FunctionDef):
            t= cls.function_def_check_type(node)
        elif isinstance(node, Params):
            t= cls.params_check_type(node)
        elif isinstance(node, FunctionCall):
            t= cls.function_call_check_type(node)
        elif isinstance(node, ExpressionBlock):
            t= cls.expression_block_check_type(node)
        elif isinstance(node, TrueLiteral):
            t= cls.true_check_type(node)
        elif isinstance(node, FalseLiteral):
            t= cls.false_check_type(node)
        elif isinstance(node,If):
            t= cls.if_check_type(node)
        elif isinstance(node,Case):
            t= cls.case_check_type(node)
        elif isinstance(node, While):
            t= cls.while_check_type(node)
        if test_mode:
            print(f'{node}: {t}')
        return t
        
    
    def while_check_type(node: While, infered_type=[]):
        condition_type = Type_Check.check_type(node.condition,['bool'])
        body_type = Type_Check.check_type(node.body)
        return Type_Check.check_and_ret(node,body_type,infered_type)
    
    def case_check_type(node: Case, infered_type=[]):
        condition_type = Type_Check.check_type(node.condition,['bool'])
        body_type = Type_Check.check_type(node.body)
        return Type_Check.check_and_ret(node,body_type,infered_type)
        
    # To do after Case
    def if_check_type(node: If, infered_type=[]):
        pass
        
    # Not understand ExpressionBlock class
    def expression_block_check_type(node: ExpressionBlock,infered_type=[]):
        exp_list= node.exp_list
        for i in range(len(exp_list)):
            exp_type=Type_Check.check_type(exp_list[i])
            if i == len(exp_list)-1:
                return Type_Check.check_and_ret(node,exp_type,infered_type)        

    # Check that function is defined before using it
    # How to a FunctionDef node to check params types !!!!
    def function_call_check_type(node: FunctionCall,infered_type=[]):
        # func_id = node.func_id
        # params=node.params
        input_params= Type_Check.check_type(node.params)
        funct_def= node.global_definitions[f'{node.func_id.name}/{len(node.params)}']
        pass

    def params_check_type(node: Params,infered_type=[]):
        static_type= []
        for e in nodes.param_list: 
            static_type.append(Type_Check.check_type(e))
        return Type_Check.check_and_ret(node,static_type,[])

    # Clase para citar variables declaradas?
    # Si existe ver forma de usarla, si no crear una variable contexto para el chequeo de tipos
    def function_def_check_type(node: FunctionDef, infered_type=[]):
        id_type= Type_Check.check_type(node.func_id)
        params_type= Type_Check.check_type(node.params)
        infers=[]
        if id_type: infers=[id_type]
        static_type= Type_Check.check_type(node.body, infers)
        return Type_Check.check_and_ret(node,static_type,infers)

    def true_check_type(node: TrueLiteral,infered_type=[]):
        return Type_Check.check_and_ret(node,'bool',infered_type)
    
    def false_check_type(node: FalseLiteral,infered_type=[]):
        return Type_Check.check_and_ret(node,'bool',infered_type)  
    
    def sqrt_check_type(node: Sqrt, infered_type=[]):
        static_type= 'number'
        return Type_Check.check_and_ret(node, static_type, infered_type)

    def sin_check_type(node: Sin, infered_type=[]):
        static_type= 'number'
        return Type_Check.check_and_ret(node, static_type, infered_type)

    def e_check_type(node: E, infered_type=[]):
        static_type= 'number'
        return Type_Check.check_and_ret(node, static_type, infered_type)

    def pi_check_type(node: Pi, infered_type=[]):
        static_type= 'number'
        return Type_Check.check_and_ret(node, static_type, infered_type)

    def rand_check_type(node: Rand, infered_types=[]):
        static_type= 'number'
        return Type_Check.check_and_ret(node,static_type,infered_types)

    def cos_check_type(node: Cos, infered_types=[]):
        static_type= Type_Check.check_type(node.value, ['number'])
        return Type_Check.check_and_ret(node,static_type,infered_types)

    def log_check_type(node: Log, infered_types=[]):
        static_type= Type_Check.check_type(node.value, ['number'])
        base = Type_Check.check_type(node.base, ['number'])
        return Type_Check.check_and_ret(node,static_type,infered_types)

    def exp_check_type(node: Exp,infered_types=[]):
        static_type= Type_Check.check_type(node.value, ['number'])
        return Type_Check.check_and_ret(node,static_type,infered_types)

    def binop_check_type(node: BinOp,infered_types=[]):
        left_type = Type_Check.check_type(node.left)
        right_type = Type_Check.check_type(node.right)
        static_type=''
        # Check that the types are valid for the operation
        if node.op in ["+", "-", "*", "/", "^", "**"]:
            if left_type != "number" or right_type != "number":
                raise TypeError(f"Invalid type for operation: {node.op}")
            else: static_type= 'number'
        if node.op == "@":
            if (
                left_type != "string"
                and left_type != "number"
                or right_type != "string"
                and right_type != "number"
            ):
                raise TypeError(f"Invalid type for operation: {left_type}")
            else: static_type= 'string'
        return Type_Check.check_and_ret(node,static_type,infered_types)

    # !!!!check_type methods Not revised completely from this Point

    def print_check_type(node: Print,infered_types=[]):
        static_type= "void"
        return Type_Check.check_and_ret(node,static_type,infered_types)

    def let_check_type(node: Let, infered_types=[]):
        static_type= Type_Check.check_type(node.body)
        Type_Check.check_and_ret(node,static_type,infered_types)

    def assign_check_type(node: Assign,infered_types=[]):
        # print('in assign_check_type')
        declared_type = Type_Check.check_type(node.name)
        type = Type_Check.check_type(node.value)
        if declared_type != '':
            if (type != declared_type):
                # Exception here!!!!!!!!!!
                raise TypeError('Declared type is diferent from the type of the value given.')
        node.name.annotated_type = type
        return type

    def id_check_type(node:ID,infered_types=[]):
        return node.annotated_type

    def number_check_type(node: Num,infered_types=[]):
        node.static_type= 'number'
        return 'number'

    def string_check_type(node: StringLiteral,infered_types=[]):
        node.static_type= 'string'
        return 'string'


    # endregion
    
    def check_inference(type_val,infers: list):
            asserted=False
            for e in infers:
                if(e == type_val):
                    asserted= True
            if not asserted or len(infers)==0:
                raise Exception(f'The Type of the object cannot be of type: {type_val}')
    
    def check_and_ret(node,static_type,infers):
        Type_Check.check_inference(static_type, infers)
        node.static_type= static_type
        return static_type

    
        
        
# region old

# import hulk_parser as hp

# def check_type(node: hp.Node):
#     print('in check_type')
#     print(id(type(node)))
#     print(id(type(hp.Assign)))
#     print(isinstance(node,type(hp.Assign)))
#     print(type(node) is type(hp.Assign))
#     if isinstance(node,hp.Assign):
#         print('mark 1')
#         return assign_check_type(node)
#     elif isinstance(node, hp.Num):
#         print('mark 2')
#         return number_check_type(node)
#     elif isinstance(node, hp.StringLiteral):
#         print('mark 3')
#         return string_check_type(node)
#     elif isinstance(node, hp.Let):
#         print('mark 4')
#         let_check_type(node)
#     elif isinstance(node, hp.Print):
#         print('mark 5')
#         return print_check_type(node)
#     elif isinstance(node, hp.BinOp):
#         print('mark 6')
#         return binop_check_type(node)
#     elif isinstance(node, ID):
#         return id_check_type(node)
    
# def id_check_type(node: ID):
#     pass

# def binop_check_type(node: hp.BinOp):
#     left_type = check_type(node.left)
#     right_type = check_type(node.right)

#     # Check that the types are valid for the operation
#     if node.op in ["+", "-", "*", "/"]:
#         if left_type != "number" or right_type != "number":
#             raise TypeError(f"Invalid type for operation: {left_type}")
#         else: return 'number'
#     if node.op in ["^", "**"]:
#         if left_type != "number" or right_type != "number":
#             raise TypeError(f"Invalid type for operation: {left_type}")
#         else: return 'number'
#     if node.op == "@":
#         if (
#             left_type != "string"
#             and left_type != "number"
#             or right_type != "string"
#             and right_type != "number"
#         ):
#             raise TypeError(f"Invalid type for operation: {left_type}")
#         else: return 'string'

# def print_check_type(node: hp.Print):
#     return 'void'

# def let_check_type(node: hp.Let):
#     return check_type(node.body)

# def assign_check_type(node: hp.Assign):
#     print('in assign_check_type')
#     declared_type = node.name.opt_type
#     type = check_type(node.value)
#     if declared_type != '':
#         if (type != declared_type):
#             # Exception here!!!!!!!!!!
#             raise TypeError('Declared type is diferent from the type of the value given.')
#     node.name.opt_type = type
#     return type

# def number_check_type(node: hp.Num):
#     return 'number'

# def string_check_type(node: hp.StringLiteral):
#     return 'string'

# endregion