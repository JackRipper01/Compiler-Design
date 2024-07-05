
# region Type Checking

from hulk_ast import *

def check_type(node: Node):
    if isinstance(node,Assign):
        return assign_check_type(node)
    elif isinstance(node, Num):
        return number_check_type(node)
    elif isinstance(node, StringLiteral):
        return string_check_type(node)
    elif isinstance(node, Let):
        let_check_type(node)
    elif isinstance(node, Print):
        return print_check_type(node)
    elif isinstance(node, BinOp):
        return binop_check_type(node)
    elif isinstance(node, Exp):
        return exp_check_type(node)
    elif isinstance(node, Log):
        return log_check_type(node)
    elif isinstance(node, Cos):
        return cos_check_type(node)
    elif isinstance(node, Rand):
        return rand_check_type(node)
    elif isinstance(node, Pi):
        return pi_check_type(node)
    elif isinstance(node, E):
        return e_check_type(node)
    elif isinstance(node, Sin):
        return sin_check_type(node)
    elif isinstance(node, Sqrt):
        return sqrt_check_type(node)
    
    
def sqrt_check_type(node: Sqrt, infered_type=[]):
    static_type= 'number'
    return check_and_ret(node, static_type, infered_type)

def sin_check_type(node: Sin, infered_type=[]):
    static_type= 'number'
    return check_and_ret(node, static_type, infered_type)

def e_check_type(node: E, infered_type=[]):
    static_type= 'number'
    return check_and_ret(node, static_type, infered_type)

def pi_check_type(node: Pi, infered_type=[]):
    static_type= 'number'
    return check_and_ret(node, static_type, infered_type)

def rand_check_type(node: Rand, infered_types=[]):
    static_type= 'number'
    return check_and_ret(node,static_type,infered_types)

def cos_check_type(node: Cos, infered_types=[]):
    static_type= check_type(node.value, ['number'])
    return check_and_ret(node,static_type,infered_types)

def log_check_type(node: Log, infered_types=[]):
    static_type= check_type(node.value, ['number'])
    base = check_type(node.base, ['number'])
    return check_and_ret(node,static_type,infered_types)

def exp_check_type(node: Exp,infered_types=[]):
    static_type= check_type(node.value, ['number'])
    return check_and_ret(node,static_type,infered_types)

def binop_check_type(node: BinOp,infered_types=[]):
    left_type = check_type(node.left)
    right_type = check_type(node.right)
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
    return check_and_ret(node,static_type,infered_types)

# !!!!check_type methods Not revised completely from this Point

def print_check_type(node: Print,infered_types=[]):
    static_type= "void"
    return check_and_ret(node,static_type,infered_types)

def let_check_type(node: Let, infered_types=[]):
    static_type= check_type(node.body)
    check_and_ret(node,static_type,infered_types)

def assign_check_type(node: Assign,infered_types=[]):
    # print('in assign_check_type')
    declared_type = check_type(node.name)
    type = check_type(node.value)
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

def check_and_ret(node,static_type,infers):
    check_inference(static_type, infers)
    node.static_type= static_type
    return static_type

def check_inference(type_val,infers: list):
    asserted=False
    for e in infers:
        if(e == type_val):
            asserted= True
    if not asserted or len(infers)==0:
        raise Exception(f'The Type of the object cannot be of type: {type_val}')
    
        
        
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