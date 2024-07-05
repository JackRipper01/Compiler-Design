import graphviz
from typing import List

from hulk_ast import (
    nodes,
    FunctionCall,
    Params,
    Let,
    Assign,
    ID,
    While,
    For,
    BinOp,
)

def refact_ast(nodes_dict : dict):
    "esto convierte el for en el while equivalente y los let en los let con una sola asignacion concatenados equivalentes"
    for_expressions : List[For] = list(filter(lambda x: type(x) is For, nodes_dict.keys()))
    
    for for_item in for_expressions:
        nodes.pop(for_item)
        condition_id_iter = ID ("iterable", "")
        func_call_next_id = ID("next", "func_call")
        func_call_next_params = Params([])
        func_call_next = FunctionCall(func_call_next_id, func_call_next_params)
        condition = BinOp(condition_id_iter ,".", func_call_next)
        id_assign_inner_let = for_item.iterator
        assign_id_iter = ID ("iterable", "")
        func_call_current_id = ID("current", "func_call")
        func_call_current_params = Params([])
        func_call_current = FunctionCall(func_call_current_id, func_call_current_params)
        value_assign_inner_let = BinOp(assign_id_iter ,".", func_call_current)
        assign_inner_let = Assign(id_assign_inner_let, value_assign_inner_let)
        inner_let = Let([assign_inner_let], for_item.body)
        while_item = While(condition, inner_let)
        id_master_assign = ID ("iterable", "")
        value_master_assign = for_item.iterable
        master_assign = Assign(id_master_assign, value_master_assign)
        # master_let = Let([master_assign], while_item)
        master_let : Let = for_item.parent
        master_let.assign.append(master_assign)
        master_let.body = while_item

        func_call_next_id.parent = func_call_next
        func_call_next_params.parent = func_call_next
        condition_id_iter.parent = condition
        func_call_next.parent = condition
        func_call_current_id.parent = func_call_current
        func_call_current_params.parent = func_call_current
        assign_id_iter.parent = value_assign_inner_let
        func_call_current.parent = value_assign_inner_let
        id_assign_inner_let.parent = assign_inner_let
        value_assign_inner_let.parent = assign_inner_let
        assign_inner_let.parent = inner_let
        for_item.body.parent = inner_let
        condition.parent = while_item
        inner_let.parent = while_item
        id_master_assign.parent = master_assign
        value_master_assign.parent = master_assign
        master_assign.parent = master_let
        while_item.parent = master_let
        # master_let.parent = for_item.parent
        for_item = master_let

    let_expressions : List[Let] = list(filter(lambda x: type(x) is Let, nodes_dict.keys()))

    for let in let_expressions:
        if len(let.assign)<=1:
            # print("let is ok")
            continue

        current_let = let
        end_body = let.body
        for assign_item in (let.assign)[1:]:
            new_let = Let([assign_item], None)
            assign_item.parent = new_let
            current_let.body = new_let
            new_let.parent = current_let
            current_let = new_let
        current_let.body = end_body
        end_body.parent = current_let
        let.assign = let.assign[:1]
    return nodes_dict

def create_AST_graph(dict: dict, graph_name):
    "guarda el ast en un grafiquito guapo...si es muy grande se parte"
    dot = graphviz.Digraph(graph_name)
    for key in dict.keys():
        dot.node(str(key), dict[key])
    for key in dict.keys():
        if key.parent:
            dot.edge(str(key.parent), str(key))
    dot.render(directory="output")
    
def create_Hierarchy_graph(dict: dict, graph_name):
    "guarda la jerarquia en un grafiquito guapo...si es muy grande se parte"
    dot = graphviz.Digraph(graph_name)
    for key in dict.keys():
        dot.node(str(key), dict[key].name)
    for key in dict.keys():
        if dict[key].parent:
            dot.edge(str(dict[key].parent), str(key))
    dot.render(directory="output")
    
def set_depth(i_dict:dict, key: str, visited):
    if key in visited:
        return "Error in type definition: "+key+" appeared in class hierarchy twice"
    visited.add(key)
    for item in i_dict[key].children:
        i_dict[item].depth = i_dict[key].depth + 1
        curr = set_depth(i_dict, item, visited)
        if curr:
            return curr
        else:
            pass
        
def LCA_BI(i_dict:dict, A, B):
    if i_dict[A].depth == i_dict[B].depth:
        if A == B:
            return A
        else:
            A = i_dict[A].parent
            B = i_dict[B].parent
            return LCA_BI(i_dict, A, B)
    else:
        if i_dict[A].depth > i_dict[B].depth:
            A = i_dict[A].parent
            return LCA_BI(i_dict, A, B)
        else:
            B = i_dict[B].parent
            return LCA_BI(i_dict, A, B)
        
def LCA(i_dict, *params):
    lca = LCA_BI(i_dict, params[0], params[1])
    for i in range(1, len(params)-1):
        lca = LCA_BI(i_dict, lca, LCA_BI(i_dict, params[i], params[i+1]))
    return lca

def trasspass_params_to_children(i_dict, name:str, ast):
    forb = ["Object", "String", "Number", "Boolean"]
    
    if name not in forb:
        father_instance = ast.global_definitions[name]
        for child in i_dict[name].children:
            if child in forb:
                continue
            child_inst = ast.global_definitions[child]
            if len(child_inst.params.param_list)==0 and len(child_inst.inherits.params.param_list)==0:
                child_inst.params.param_list = father_instance.params.param_list.copy()
                new_params = []
                for i in child_inst.params.param_list:
                    new_params.append(ID(i.name, ""))
                child_inst.inherits.params.param_list = new_params
    
    for child in i_dict[name].children:
        trasspass_params_to_children(i_dict,child, ast)
        
    
    