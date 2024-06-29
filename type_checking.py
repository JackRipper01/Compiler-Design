from hulk_parser import *

def check_type(node: Node):
    if isinstance(node,Assign):
        return assign_check_type(node)
    elif isinstance(node, Num):
        return number_check_type(node)
    elif isinstance(node, StringLiteral):
        return string_check_type(node)

def assign_check_type(node: Assign):
    declared_type = node.name.split()[0]
    type = check_type(node.value)
    if declared_type != 'var':
        if (type != declared_type):
            # Exception here!!!!!!!!!!
            raise TypeError('Declared type is diferent from the type of the value given.')
    return type

def number_check_type(node: Num):
    return 'number'

def string_check_type(node: StringLiteral):
    return 'string'



