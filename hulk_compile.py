import imp
from hulk_parser import *
from hulk_ast import *

def create_AST_graph(dict: dict, graph_name):
    "guarda el ast en un grafiquito guapo...si es muy grande se parte"
    dot = graphviz.Digraph(graph_name)
    for key in dict.keys():
        if not key.parent:
            dict[key] += " ( </> )"
        dot.node(str(key), dict[key])
    for key in dict.keys():
        if key.parent:
            dot.edge(str(key.parent), str(key))
    dot.render(directory="output")


def refact_ast(nodes_dict: dict):
    "esto convierte el for en el while equivalente y los let en los let con una sola asignacion concatenados equivalentes"
    for_expressions: List[For] = list(
        filter(lambda x: type(x) is For, nodes_dict.keys())
    )

    for for_item in for_expressions:
        nodes.pop(for_item)
        condition_id_iter = ID("iterable", "")
        func_call_next_id = ID("next", "func_call")
        func_call_next_params = Params([])
        func_call_next = FunctionCall(func_call_next_id, func_call_next_params)
        condition = BinOp(condition_id_iter, ".", func_call_next)
        id_assign_inner_let = for_item.iterator
        assign_id_iter = ID("iterable", "")
        func_call_current_id = ID("current", "func_call")
        func_call_current_params = Params([])
        func_call_current = FunctionCall(func_call_current_id, func_call_current_params)
        value_assign_inner_let = BinOp(assign_id_iter, ".", func_call_current)
        assign_inner_let = Assign(id_assign_inner_let, value_assign_inner_let)
        inner_let = Let([assign_inner_let], for_item.body)
        while_item = While(condition, inner_let)
        id_master_assign = ID("iterable", "")
        value_master_assign = for_item.iterable
        master_assign = Assign(id_master_assign, value_master_assign)
        # master_let = Let([master_assign], while_item)
        master_let: Let = for_item.parent
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

    let_expressions: List[Let] = list(
        filter(lambda x: type(x) is Let, nodes_dict.keys())
    )

    for let in let_expressions:
        if len(let.assign) <= 1:
            # print("let is ok")
            continue

        current_let = let
        end_body = let.body
        for assign_item in (let.assign)[1:]:
            new_let = Let(assign_item, None)
            assign_item.parent = new_let
            current_let.body = new_let
            new_let.parent = current_let
            current_let = new_let
        current_let.body = end_body
        end_body.parent = current_let
        let.assign = let.assign[:1]


def hulk_parse(code):
    "parsea el codigo de hulk, retornando la raiz del ast"
    parser = yacc.yacc(start="program", method="LALR")

    AST = parser.parse(code)
    create_AST_graph(nodes, "AST")
    if len(sErrorList) == 0:
        print("SUCCESS PARSING!!")
        return AST
    else:
        print("\nPARSING FINISHED WITH ERRORS:")
        for i in sErrorList:
            if i:
                print(
                    " - ",
                    f"Syntax error near '{i.value}' at line {i.lineno}, column {find_column(code,i)}",
                )
            else:
                print("Syntax error at EOF")
            break

        return None


if __name__ == "__main__":
    # code = io.open("input/custom_test.hulk").read()
    # print(code)
    # type PolarPoint inherits Point {
    # rho() => sqrt(self.getX() ^ 2 + self.getY() ^ 2);
    # }
    code = """
    type Point(x,y) {
    x = x;
    y = y;

    getX() => self.x;
    getY() => self.y;

    setX(x) => self.x := x;
    setY(y) => self.y := y;
    }
    
    type PolarPoint inherits Point {
    rho()=>self.x+10;
    }
    4;
"""
    hulk_parse(code)
