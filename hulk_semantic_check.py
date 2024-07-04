# region temp import 
from hulk_parser import hulk_parse
from misc import set_depth, LCA, create_Hierarchy_graph
# endregion

import visitor

from hulk_ast import (
    Node,
    Program,
    FunctionDef,
    FunctionCall,
    Params,
    ExpressionBlock,
    Let,
    Assign,
    ID,
    If,
    Case,
    While,
    For,
    TrueLiteral,
    FalseLiteral,
    TypeDef,
    TypeCall,
    Protocol,
    VectorExt,
    VectorInt,
    VectorCall,
    BinOp,
    UnaryOp,
    Num,
    StringLiteral,
    Pi,
    E,
    Print,
    Sqrt,
    Sin,
    Cos,
    Exp,
    Log,
    Rand,
)

class HierarchyNode:
    def __init__(self, name, parent, children, depth):
        self.name = name
        self.parent = parent
        self.children = children
        self.depth = depth
        

class ScopeBuilder:
    def __init__(self):
        self.errors = []

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node):
        node.a = "bu ja ja"
    
    def get_global_definitions(self, ast_input : Program):
        ast_input.global_definitions["Number"] = "float"
        ast_input.global_definitions["String"] = "string"
        ast_input.global_definitions["Boolean"] = "int"
        
        for function in ast_input.functions:
            function_name = function.func_id.name+"/"+str(len(function.params.param_list))
            if function_name in ast_input.global_definitions:
                self.errors.append("Function "+ function_name +" already defined: ")
            else:
                ast_input.global_definitions[function_name] = function
        
        for type_def in list(ast_input.types)+list(ast_input.protocols):
            type_name = type_def.id.name
            if type_name in ast_input.global_definitions:
                self.errors.append("Type "+ type_name+" already defined: ")
            else:
                ast_input.global_definitions[type_name] = type_def
    
    def hierarchy_tree_build(self, ast_root: Program):
        hierarchy_tree = {}
        hierarchy_tree["Object"] = HierarchyNode("Object", None, [], 0)
        hierarchy_tree["Number"] = HierarchyNode("Number","Object",[],1)
        hierarchy_tree["String"] = HierarchyNode("String","Object",[],1)
        hierarchy_tree["Boolean"] = HierarchyNode("Boolean","Object",[],1)
        hierarchy_tree["Object"].children.append("Number")
        hierarchy_tree["Object"].children.append("String")
        hierarchy_tree["Object"].children.append("Boolean")
        
        for type_name in ast_root.types: 
            hierarchy_tree[type_name.id.name] = HierarchyNode(type_name.id.name, None, [], 0)
            
        for type_name in ast_root.types:
            current_type = type_name.id.name
            
            if type_name.inherits:
                inherits_from = type_name.inherits.id.name
                if type(ast_root.global_definitions[inherits_from]) is str:
                    self.errors.append("Cannot inherit from type "+inherits_from)
                    continue
                hierarchy_tree[current_type].parent = inherits_from
                hierarchy_tree[inherits_from].children.append(current_type)
            else:
                hierarchy_tree[current_type].parent = "Object"
                hierarchy_tree["Object"].children.append(current_type)
        print(*[str(x)+str(hierarchy_tree[x].children) for x in hierarchy_tree], sep="\n")
        err = set_depth(hierarchy_tree, "Object", set())
        if err:
            self.errors.append(err)
        return hierarchy_tree

        
    def check_tree(self, i_dict, root):
        qww = [root]
        visited = set()
        while len(qww)>0:
            current = qww.pop(0)
            visited.add(current)
            for child in i_dict[current].children:
                if child in visited:
                    self.errors.append("Error en la definicion del tipo: "+child)
                else:
                    qww.append(child)
        if len(visited) != len(i_dict):
            self.errors.append("Error en la definicion de tipos involucrando a los tipos: "+str(set(i_dict).difference(visited)))
    
                
def semantic_check(ast: Program):
    SB = ScopeBuilder()
    SB.get_global_definitions(ast)
    HierarchyTypes = SB.hierarchy_tree_build(ast)
    create_Hierarchy_graph(HierarchyTypes, "HG")
    
    SB.check_tree(HierarchyTypes, "Object")
    # print(LCA(HierarchyTypes, "Canino","Perro","Lobo"))
    
    
    print(SB.errors)
    # your code here



if __name__ == "__main__":
    ast,_ = hulk_parse(r"""type Animal{}
                               type Felino inherits Animal{}
                               type Gato inherits Felino {}
                               type Canino inherits Animal{}
                               type Perro inherits Canino {}
                               type Lobo inherits Canino{}
                               """, create_graph=True)
    semantic_check(ast)
    