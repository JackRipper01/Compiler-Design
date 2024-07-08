# region temp import
from ast import Param
from hulk_lexer import errorList as lexerErrors
from hulk_parser import hulk_parse
from misc import set_depth, LCA, create_Hierarchy_graph, ColumnFinder, get_descendancy

from ply.yacc import YaccSymbol

# endregion

import visitor

from hulk_ast import (
    Node,  # NAN
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
    For,  # NAN
    TrueLiteral,  # NAN
    FalseLiteral,  # NAN
    TypeDef,
    TypeCall,
    Protocol,
    VectorExt,
    VectorInt,
    VectorCall,
    BinOp,
    UnaryOp,
    Num,  # NAN
    StringLiteral,  # NAN
    Pi,  # NAN
    E,  # NAN
    Print,
    Sqrt,
    Sin,
    Cos,
    Exp,
    Log,
    Rand,  # NAN
)

# TypeColector
# TypeBuilder
# SemanticCheck
# TypeCheck?

cf =ColumnFinder()

class HierarchyNode:
    def __init__(self, name, parent, children, depth):
        self.name = name
        self.parent = parent
        self.children = children
        self.depth = depth


class ScopeBuilder:
    def __init__(self):
        self.errors = []
        self.on_type = False
        self.on_function = False
        self.current = ""  # desarrollar idea

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node: Program):

        self.get_global_definitions(node)
        self.hierarchy_tree_build(node)
        self.check_tree(node, "Object")
        self.trasspass_params_to_children(node, "Object", set())
        print([x for x in get_descendancy(node, "Object")])
        
        self.on_function = True
        for function in node.functions:
            function: FunctionDef
            function.variable_scope = node.variable_scope
            self.visit(function)
        self.on_function = False

        self.on_type = True
        for type_str in node.hierarchy_tree["Object"].children:
            if not type_str in ["Number", "String", "Boolean"]:
                node.global_definitions[type_str].variable_scope = node.variable_scope
                self.current = type_str
                self.visit(node.global_definitions[type_str])
        self.current = ""
        self.on_type = False

        if node.global_exp:
            node.global_exp.variable_scope = node.variable_scope
            self.visit(node.global_exp)
        else:
            self.errors.append(("Missing Global Expression"))

    @visitor.when(TypeDef)
    def visit(self, node: TypeDef):
        node.variable_scope = node.variable_scope.copy()

        for param in node.params.param_list:
            param: ID
            node.variable_scope[param.name] = param
            self.check_annotation(param)

        if node.inherits:
            node.inherits.variable_scope = node.variable_scope
            self.visit(node.inherits)
        
        
        for assign in node.variables:
            assign: Assign
            assig_name = self.assign_name_getter(assign, True)
            if assig_name in node.variable_scope:
                self.errors.append(
                    f"Private var '{assign.name.name}' already defined in type '{self.current}'{cf.add_line_column(assign.name.name)}"
            )
            node.variable_scope[assig_name] = assign.name

        self.on_function = True
        this_fx_scope = set()
        for method in node.functions:
            method: FunctionDef
            method_name = self.method_name_getter(method, True)
            if method_name in this_fx_scope:
                self.errors.append(
                    f"Method '{self.method_name_getter(method)}' already defined in type '{self.current}'"+cf.add_line_column(method.func_id.name)
                )
            this_fx_scope.add(method_name)
            node.variable_scope[method_name] = method
        self.on_function = False

        for assign in node.variables:
            assign: Assign
            assign.variable_scope = node.variable_scope
            self.visit(assign)
        for key in node.variable_scope.copy():
            key: str
            if not key.endswith("/private"):
                node.variable_scope.pop(key)

        # self.on_function = True
        # for method in node.functions:
        #     method: FunctionDef
        #     method.variable_scope = node.variable_scope

        #     method.variable_scope["self"] = node
        #     self.visit(method)
        # self.on_function = False

        for child in node.hierarchy_tree[node.id.name].children:
            node.global_definitions[child].variable_scope = node.variable_scope
            self.current = child
            self.visit(node.global_definitions[child])

    @visitor.when(FunctionDef)
    def visit(self, node: FunctionDef):
        node.variable_scope = node.variable_scope.copy()
        for param in node.params.param_list:
            param: ID
            self.check_annotation(param)
            node.variable_scope[param.name] = param
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)

    @visitor.when(Print)
    def visit(self, node: Print):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(Sqrt)
    def visit(self, node: Sqrt):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(Sin)
    def visit(self, node: Sin):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(Cos)
    def visit(self, node: Cos):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(Exp)
    def visit(self, node: Exp):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(Log)
    def visit(self, node: Log):
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(ID)
    def visit(self, node: ID):
        if node.name not in node.variable_scope:
            self.errors.append("Variable '" + node.name + "' not defined"+cf.add_line_column(node.name))

    @visitor.when(Params)
    def visit(self, node: Params):
        for param in node.param_list:
            param.variable_scope = node.variable_scope
            self.visit(param)

    @visitor.when(BinOp)
    def visit(self, node: BinOp):

        if node.op in [
            "+",
            "-",
            "*",
            "/",
            "%",
            ">",
            "<",
            ">=",
            "<=",
            "==",
            "!=",
            "^",
            "**",
            "AD",
            "@",
            "@@",
        ]:
            node.left.variable_scope = node.variable_scope
            self.visit(node.left)
            node.right.variable_scope = node.variable_scope
            self.visit(node.right)

        elif node.op == ".":
            node.left.variable_scope = node.variable_scope
            self.visit(node.left)
            if self.on_type and self.on_function:
                pass
                # check context from class
            else:
                if not (type(node.right) is FunctionCall):
                    self.errors.append(
                        "Invalid access to private member '"
                        + node.right.name
                        + "' outside method class declaration"+cf.add_line_column(node.right.name)
                    )
                else:
                    node.left.variable_scope = node.variable_scope
                    self.visit(node.left)
                    node.right.params.variable_scope = node.variable_scope
                    self.visit(node.right.params)
        elif node.op in ["is","as"]:
            if node.right.annotated_type not in node.hierarchy_tree:
                self.errors.append("Type '"+node.right.annotated_type+"' undefined"+cf.add_line_column(node.right.name))
            node.left.variable_scope = node.variable_scope
            self.visit(node.left)
        else:
            node.right.variable_scope = node.variable_scope
            self.visit(node.right)

    @visitor.when(UnaryOp)
    def visit(self, node: UnaryOp):
        node.operand.variable_scope = node.variable_scope
        self.visit(node.operand)

    @visitor.when(VectorExt)
    def visit(self, node: VectorExt):
        for item in node.items:
            item.variable_scope = node.variable_scope
            self.visit(item)
    
    @visitor.when(VectorInt)
    def visit(self, node: VectorInt):
        node.variable_scope = node.variable_scope.copy()
        
        node.iterable.variable_scope = node.variable_scope
        self.visit(node.iterable)
        
        node.variable_scope[node.iterator.name] = node.iterator
        
        node.expression.variable_scope = node.variable_scope
        self.visit(node.expression)      

    @visitor.when(VectorCall)
    def visit(self, node: VectorCall):
        node.id.variable_scope = node.variable_scope
        self.visit(node.id)

        node.index.variable_scope = node.variable_scope
        self.visit(node.index)

    @visitor.when(FunctionCall)
    def visit(self, node: FunctionCall):
        fn_name = node.func_id.name + "/" + str(len(node.params.param_list))
        if fn_name not in node.global_definitions:
            self.errors.append("Function " + fn_name + " not defined")
        node.params.variable_scope = node.variable_scope
        self.visit(node.params)

    @visitor.when(TypeCall)
    def visit(self, node: TypeCall):
        if node.id.name in node.global_definitions:
            if len(node.params.param_list) != len(
                node.global_definitions[node.id.name].params.param_list
            ):
                self.errors.append(
                    "Amount of params doesnt match type definition of "
                    + node.id.name
                    + " ("
                    + str(len(node.global_definitions[node.id.name].params.param_list))
                    + f") (line {node.global_definitions[node.id.name].id.name.lineno}) and its instanstiation ("
                    + str(len(node.params.param_list))
                    + ")"+cf.add_line_column(node.id.name)
                )
            node.params.variable_scope = node.variable_scope
            self.visit(node.params)
        else:
            self.errors.append("Type " + node.id.name + " not defined")

    @visitor.when(ExpressionBlock)
    def visit(self, node: ExpressionBlock):
        for exp in node.exp_list:
            exp.variable_scope = node.variable_scope
            self.visit(exp)

    @visitor.when(Assign)
    def visit(self, node: Assign):
        self.check_annotation(node.name)
        node.value.variable_scope = node.variable_scope
        self.visit(node.value)

    @visitor.when(If)
    def visit(self, node: If):
        for case_item in node.case_list:
            case_item.variable_scope = node.variable_scope
            self.visit(case_item)

    @visitor.when(While)
    def visit(self, node: While):
        node.condition.variable_scope = node.variable_scope
        self.visit(node.condition)
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)

    @visitor.when(Case)
    def visit(self, node: Case):
        node.condition.variable_scope = node.variable_scope
        self.visit(node.condition)
        node.body.variable_scope = node.variable_scope
        self.visit(node.body)

    @visitor.when(Let)
    def visit(self, node: Let):
        node.assign[0].variable_scope = node.variable_scope
        self.visit(node.assign[0])
        node.variable_scope = node.variable_scope.copy()
        assig_name = self.assign_name_getter(node.assign[0])
        node.variable_scope[assig_name] = node.assign[0].name

        node.body.variable_scope = node.variable_scope
        self.visit(node.body)

    def get_global_definitions(self, ast_input: Program):
        ast_input.global_definitions["Object"] = "void"
        ast_input.global_definitions["Number"] = "float"
        ast_input.global_definitions["String"] = "string"
        ast_input.global_definitions["Boolean"] = "int"

        for function in ast_input.functions:
            function_name = (
                function.func_id.name + "/" + str(len(function.params.param_list))
            )
            if function_name in ast_input.global_definitions:
                self.errors.append("Function " + function_name + " already defined")
            else:
                ast_input.global_definitions[function_name] = function

        for type_def in list(ast_input.types) + list(ast_input.protocols):
            type_name = type_def.id.name
            if type_name in ast_input.global_definitions:
                self.errors.append("Type " + type_name + " already defined: ")
            else:
                ast_input.global_definitions[type_name] = type_def

    def hierarchy_tree_build(self, ast_root: Program):
        hierarchy_tree = ast.hierarchy_tree
        hierarchy_tree["Object"] = HierarchyNode("Object", None, [], 0)
        hierarchy_tree["Number"] = HierarchyNode("Number", "Object", [], 1)
        hierarchy_tree["String"] = HierarchyNode("String", "Object", [], 1)
        hierarchy_tree["Boolean"] = HierarchyNode("Boolean", "Object", [], 1)
        hierarchy_tree["Object"].children.append("Number")
        hierarchy_tree["Object"].children.append("String")
        hierarchy_tree["Object"].children.append("Boolean")

        for type_name in ast_root.types:
            hierarchy_tree[type_name.id.name] = HierarchyNode(
                type_name.id.name, None, [], 0
            )

        for type_name in ast_root.types:
            current_type = type_name.id.name

            if type_name.inherits:
                inherits_from = type_name.inherits.id.name
                if inherits_from in ast_root.global_definitions:
                    if (
                        type(ast_root.global_definitions[inherits_from]) is str
                        or inherits_from not in hierarchy_tree
                    ):
                        self.errors.append(
                            "Cannot inherit from '" + inherits_from + f"' at line {type_name.id.name.lineno}"
                        )
                        continue
                    hierarchy_tree[current_type].parent = inherits_from
                    hierarchy_tree[inherits_from].children.append(current_type)
                else:
                    self.errors.append(
                        "Cannot inherit from "
                        + inherits_from
                        + " because it is not defined at line "+str(type_name.id.name.lineno)
                    )
            else:
                hierarchy_tree[current_type].parent = "Object"
                hierarchy_tree["Object"].children.append(current_type)
        err = set_depth(hierarchy_tree, "Object", set())
        if err:
            self.errors.append(err)
        return hierarchy_tree

    def check_tree(self, ast_root: Program, root):
        i_dict = ast_root.hierarchy_tree
        qww = [root]
        visited = set()
        while len(qww) > 0:
            current = qww.pop(0)
            visited.add(current)
            for child in i_dict[current].children:
                if child in visited:
                    self.errors.append("Error in type definition: " + child)
                    break
                else:
                    qww.append(child)
        if len(visited) != len(i_dict):
            self.errors.append(
                "Error in type definition: " + str(set(i_dict).difference(visited))
            )

    def check_annotation(self, var: ID):
        if (
            var.annotated_type != ""
            and var.annotated_type not in var.global_definitions
        ):
            self.errors.append(
                "Variable '"
                + var.name
                + "' annotated type '"
                + var.annotated_type
                + "' does not exist in global context"
            )

    def method_name_getter(self, function, private=False):
        if private:
            return (
                function.func_id.name
                + "/"
                + str(len(function.params.param_list))
                + "/private"
            )
        else:
            return function.func_id.name + "/" + str(len(function.params.param_list))

    def assign_name_getter(self, assign: Assign, private=False):
        if private:
            return assign.name.name + "/private"
        else:
            return assign.name.name
    
    def trasspass_params_to_children(self, ast, name:str, visited):
        forb = ["Object", "String", "Number", "Boolean"]
        
        if name in visited:
            return "Error in type definition: "+name+" appeared in class hierarchy twice"
        visited.add(name)
        
        if name not in forb:
            father_instance = ast.global_definitions[name]
            for child in ast.hierarchy_tree[name].children:
                if child in forb:
                    continue
                child_inst = ast.global_definitions[child]
                if len(child_inst.params.param_list)==0 and len(child_inst.inherits.params.param_list)==0:
                    child_inst.params.param_list = father_instance.params.param_list.copy()
                    new_params = []
                    for i in child_inst.params.param_list:
                        new_params.append(ID(i.name, ""))
                    child_inst.inherits.params.param_list = new_params
        
        for child in ast.hierarchy_tree[name].children:
            self.trasspass_params_to_children(ast,child, visited)


def semantic_check(ast: Program):
    scope_visitor = ScopeBuilder()
    scope_visitor.visit(ast)
    
    # your code here

    return ast, scope_visitor.errors


if __name__ == "__main__":
    ast, parsingErrors, _b = hulk_parse(
        r"""type Animal(){
            x = {{{{{2;}}}}};
            asd(y) => print(self.y);
            
        };
            type Felino(x) inherits Animal(){}
            type Gato(x) inherits Felino(x) {}
            type Canino(x : Object) inherits Animal{
                asd(y) => print(self.y);
            }
            
            type Perro inherits Canino {}
            type Lobo inherits Perro{}
            function asd(a,b,c) => print(b);
            let a :Number = true, b: Number = a in {print(new Lobo(6).x());
            asd(1, 2, 3); [a || x in b];(2+2); 2 is Number;}""",
            cf
    )

    print(
        "LEXER FOUND THE FOLLOWING ERRORS:" if len(lexerErrors) > 0 else "LEXING OK!",
        *lexerErrors,
        sep="\n - "
    )
    print(
        (
            "PARSER FOUND THE FOLLOWING ERRORS:"
            if len(parsingErrors) > 0
            else "PARSING OK!!"
        ),
        *parsingErrors,
        sep="\n - "
    )
    if ast:
        ast, semantic_check_errors = semantic_check(ast)

        print(
            (
                "SEMANTIC CHECK FOUND THE FOLLOWING ERRORS:"
                if len(semantic_check_errors) > 0
                else "SEMANTIC CHECK OK!!!"
            ),
            *semantic_check_errors,
            sep="\n - "
        )
