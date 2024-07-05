
# region Type Checking

from hulk_ast import *

def check_type(node: Node):
    # print('in check_type')
    # print(type(node))
    if isinstance(node,Assign):
        # print('mark 1')
        return assign_check_type(node)
    elif isinstance(node, Num):
        # print('mark 2')
        return number_check_type(node)
    elif isinstance(node, StringLiteral):
        # print('mark 3')
        return string_check_type(node)
    elif isinstance(node, Let):
        # print('mark 4')
        let_check_type(node)
    elif isinstance(node, Print):
        # print('mark 5')
        return print_check_type(node)
    elif isinstance(node, BinOp):
        # print('mark 6')
        return binop_check_type(node)
#     elif isinstance(node, ID):
#         return id_check_type(node)
    
# def id_check_type(node: ID):
#     pass

def binop_check_type(node: BinOp):
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
    node.static_type=static_type
    
def print_check_type(node: Print):
    node.static_type= "void"

def let_check_type(node: Let):
    node.static_type= check_type(node.body)

def assign_check_type(node: Assign):
    # print('in assign_check_type')
    declared_type = check_type(node.name)
    type = check_type(node.value)
    if declared_type != '':
        if (type != declared_type):
            # Exception here!!!!!!!!!!
            raise TypeError('Declared type is diferent from the type of the value given.')
    node.name.opt_type = type
    return type

def id_check_type(node:ID):
    if not node.opt_type:
        node.static_type= node.parent
    else: node.static_type= node.opt_type

def number_check_type(node: Num):
    node.static_type= 'number'

def string_check_type(node: StringLiteral):
    node.static_type= 'string'


# endregion

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