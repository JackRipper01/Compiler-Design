# region temp import
from ast import Param
from hulk_lexer import errorList as lexerErrors
from hulk_parser import hulk_parse
from misc import (
    ColumnFinder,
    HierarchyNode,
    StringToken,
    set_depth,
    LCA,
    conforms,
    get_descendancy_set,
    method_name_getter,
    assign_name_getter,
    typeof,
    create_Hierarchy_graph,
    func_conforms
)
import io

# endregion

import visitor

from hulk_ast import (
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

# TypeColector
# TypeBuilder
# SemanticCheck
# TypeCheck?

cf = ColumnFinder()


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
        self.protocol_hierarchy_build(node)
        self.check_tree(node, "Object")
        self.trasspass_params_to_children(node, "Object", set())

        # for i in node.hierarchy_tree:
        #     for j in node.hierarchy_tree:
        #         print(i,"to" ,j, conforms(node, i , j))

        self.on_function = True
        for function in node.functions:
            function: FunctionDef
            function.variable_scope = node.variable_scope
            self.visit(function)
        self.on_function = False

        self.on_type = True
        for type_str in node.hierarchy_tree["Object"].children:
            if not type_str in ["Number", "String", "Boolean", "Vector"]:
                node.global_definitions[type_str].variable_scope = node.variable_scope
                self.current = type_str
                self.visit(node.global_definitions[type_str])
        self.current = ""
        self.on_type = False
    
        
        for protocol in node.protocol_hierarchy["Empty"].children:
            node.global_definitions[protocol].variable_scope = node.variable_scope
            self.current = protocol
            self.visit(node.global_definitions[protocol])
        self.current = ""

        if node.global_exp:
            node.global_exp.variable_scope = node.variable_scope
            self.visit(node.global_exp)
        else:
            self.errors.append(("Missing Global Expression"))

    @visitor.when(Protocol)
    def visit(self, node: Protocol):
        node.variable_scope = node.variable_scope.copy()
        for meth in node.functions:
            meth: FunctionDef
            meth_name = method_name_getter(meth, True)
            if meth_name in node.variable_scope:
                self.errors.append(f"Protocol {node.id.name} reimplements method {meth.func_id.name}"+cf.add_line_column(meth.func_id.name))
            node.variable_scope[meth_name] = meth
            meth.static_type = meth.func_id.annotated_type
            
        for child in node.protocol_hierarchy[node.id.name].children:
            node.global_definitions[child].variable_scope = node.variable_scope
            self.current = child
            self.visit(node.global_definitions[child])
        
        
    @visitor.when(TypeDef)
    def visit(self, node: TypeDef):
        node.variable_scope = node.variable_scope.copy()

        for param in node.params.param_list:
            param: ID
            node.variable_scope[param.name] = param
            self.check_annotation(param)
                    
        self.chech_params_different(node.params)

        if node.inherits:
            node.inherits.variable_scope = node.variable_scope.copy()
            self.visit(node.inherits)

        for assign in node.variables:
            assign: Assign
            assig_name = assign_name_getter(assign, True)
            if assig_name in node.variable_scope:
                self.errors.append(
                    f"Private var '{assign.name.name}' already defined in type '{self.current}'{cf.add_line_column(assign.name.name)}"
                )
            node.variable_scope[assig_name] = assign.name

        self.on_function = True
        this_fx_scope = set()
        for method in node.functions:
            method: FunctionDef
            method_name = method_name_getter(method, True)
            if method_name in this_fx_scope:
                self.errors.append(
                    f"Method '{method_name_getter(method)}' already defined in type '{self.current}'"
                    + cf.add_line_column(method.func_id.name)
                )
            this_fx_scope.add(method_name)
            node.variable_scope[method_name] = method
        self.on_function = False

        for assign in node.variables:
            assign: Assign
            assign.variable_scope = node.variable_scope
            self.visit(assign)
        
        functions_scope = node.variable_scope.copy()
        for key in functions_scope.copy():
            key: str
            if not key.endswith("/private"):
                functions_scope.pop(key)

        self.on_function = True
        for method in node.functions:
            method: FunctionDef
            method.variable_scope = functions_scope.copy()
            method.variable_scope["self"] = node
            if node.inherits:
                method_name = method_name_getter(method, True)
                if (
                    method_name
                    in node.global_definitions[node.inherits.id.name].variable_scope
                ):
                    method.variable_scope["base/"+str(len(method.params.param_list))] = node.global_definitions[
                        node.inherits.id.name
                    ].variable_scope[method_name]
            self.visit(method)
        self.on_function = False

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
        self.chech_params_different(node.params)
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
            self.errors.append(
                "Variable '"
                + node.name
                + "' not defined"
                + cf.add_line_column(node.name)
            )

    @visitor.when(Params)
    def visit(self, node: Params):
        for param in node.param_list:
            param.variable_scope = node.variable_scope
            self.visit(param)

    @visitor.when(UnaryOp)
    def visit(self, node: UnaryOp):
        node.operand.variable_scope = node.variable_scope
        self.visit(node.operand)

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
            "|",
            "&",
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
                if type(node.right) is FunctionCall:
                    node.right.params.variable_scope = node.variable_scope
                    self.visit(node.right.params)
            else:
                if type(node.right) is FunctionCall:
                    node.right.params.variable_scope = node.variable_scope
                    self.visit(node.right.params)
                else:
                    self.errors.append(
                        "Invalid access to private member '"
                        + node.right.name
                        + "' outside method class declaration"
                        + cf.add_line_column(node.right.name)
                    )
        elif node.op in ["is", "as"]:
            if node.right.annotated_type not in node.hierarchy_tree:
                self.errors.append(
                    "Type '"
                    + node.right.annotated_type
                    + "' undefined"
                    + cf.add_line_column(node.right.name)
                )
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
        for item in node.items.param_list:
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
        if self.on_type and self.on_function:
            if (
                fn_name not in node.variable_scope
                and fn_name not in node.global_definitions
            ):
                self.errors.append(
                    "Function "
                    + fn_name
                    + " not defined"
                    + cf.add_line_column(node.func_id.name)
                )
        else:
            if fn_name not in node.global_definitions:
                if (
                    fn_name not in node.variable_scope
                    and fn_name not in node.global_definitions
                ):
                    self.errors.append(
                        "Function "
                        + fn_name
                        + " not defined"
                        + cf.add_line_column(node.func_id.name)
                    )
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
                    + ")"
                    + cf.add_line_column(node.id.name)
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
        assig_name = assign_name_getter(node.assign[0])
        node.variable_scope[assig_name] = node.assign[0].name

        node.body.variable_scope = node.variable_scope
        self.visit(node.body)

    def get_global_definitions(self, ast_input: Program):
        ast_input.global_definitions["Object"] = "void"
        ast_input.global_definitions["Number"] = "float"
        ast_input.global_definitions["String"] = "string"
        ast_input.global_definitions["Boolean"] = "int"
        ast_input.global_definitions["Vector"] = "vec"

        for function in ast_input.functions:
            function_name = (
                function.func_id.name + "/" + str(len(function.params.param_list))
            )
            if function_name in ast_input.global_definitions:
                self.errors.append(
                    "Function "
                    + function_name
                    + " already defined"
                    + cf.add_line_column(
                        ast_input.global_definitions[function_name].func_id.name
                    )
                )
            else:
                ast_input.global_definitions[function_name] = function

        for type_def in list(ast_input.types) + list(ast_input.protocols):
            type_name = type_def.id.name
            if type_name in ast_input.global_definitions:
                self.errors.append(
                    "Type "
                    + type_name
                    + " already defined"
                    + cf.add_line_column(type_def.id.name)
                )
            else:
                ast_input.global_definitions[type_name] = type_def

    def hierarchy_tree_build(self, ast_root: Program):
        hierarchy_tree = ast_root.hierarchy_tree
        hierarchy_tree["Object"] = HierarchyNode("Object", None, [], 0)
        hierarchy_tree["Number"] = HierarchyNode("Number", "Object", [], 1)
        hierarchy_tree["String"] = HierarchyNode("String", "Object", [], 1)
        hierarchy_tree["Boolean"] = HierarchyNode("Boolean", "Object", [], 1)
        hierarchy_tree["Vector"] = HierarchyNode("Vector", "Object", [], 1)
        hierarchy_tree["Object"].children.append("Number")
        hierarchy_tree["Object"].children.append("String")
        hierarchy_tree["Object"].children.append("Boolean")
        hierarchy_tree["Object"].children.append("Vector")

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
                            "Cannot inherit from '"
                            + inherits_from
                            + f"' at line {type_name.id.name.lineno}"
                        )
                        continue
                    hierarchy_tree[current_type].parent = inherits_from
                    hierarchy_tree[inherits_from].children.append(current_type)
                else:
                    self.errors.append(
                        "Cannot inherit from "
                        + inherits_from
                        + " because it is not defined at line "
                        + str(type_name.id.name.lineno)
                    )
            else:
                hierarchy_tree[current_type].parent = "Object"
                hierarchy_tree["Object"].children.append(current_type)
        err = set_depth(hierarchy_tree, "Object", set())
        if err:
            self.errors.append(err)
        return hierarchy_tree

    def protocol_hierarchy_build(self, ast_root: Program):  # pendiente
        hierarchy_tree = ast_root.protocol_hierarchy
        hierarchy_tree["Empty"] = HierarchyNode("Empty", None, [], 0)

        for protocol in ast_root.protocols:
            protocol : Protocol
            hierarchy_tree[protocol.id.name] = HierarchyNode(
                protocol.id.name, None, [], 0
            )

        for protocol in ast_root.protocols:
            current = protocol.id.name

            if protocol.extends:
                extend_from = protocol.extends.name
                if extend_from in ast_root.global_definitions:
                    if (
                        type(ast_root.global_definitions[extend_from]) is str
                        or extend_from not in hierarchy_tree
                    ):
                        self.errors.append(
                            "Cannot extend '"
                            + extend_from
                            + f"' at line {protocol.id.name.lineno}"
                        )
                        continue
                    hierarchy_tree[current].parent = extend_from
                    hierarchy_tree[extend_from].children.append(current)
                else:
                    self.errors.append(
                        "Cannot extend '"
                        + extend_from
                        + "' because it is not defined at line "
                        + str(protocol.id.name.lineno)
                    )
            else:
                hierarchy_tree[current].parent = "Empty"
                hierarchy_tree["Empty"].children.append(current)
        err = set_depth(hierarchy_tree, "Empty", set())
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
                else:
                    qww.append(child)
        if len(visited) != len(i_dict):
            self.errors.append(
                "Error in type definitions: "
                + str([str(x) for x in set(i_dict).difference(visited)])
                .removeprefix("[")
                .removesuffix("]")
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

    def chech_params_different(self, params: Params):
        prms = set()
        for param in params.param_list:
            if param.name in prms:
                self.errors.append(f"Param '{param.name}' already in use"+cf.add_line_column(param.name))
            prms.add(param.name)

    def trasspass_params_to_children(self, ast: Program, name: str, visited):
        forb = ["Object", "String", "Number", "Boolean", "Vector"]

        if name in visited:
            self.errors.append(
                "Error in type definition: "
                + name
                + " appeared in class hierarchy twice"
                + cf.add_line_column(ast.global_definitions[name].id.name)
            )
        visited.add(name)

        if name not in forb:
            father_instance = ast.global_definitions[name]
            for child in ast.hierarchy_tree[name].children:
                if child in forb:
                    continue
                child_inst = ast.global_definitions[child]
                if (
                    len(child_inst.params.param_list) == 0
                    and len(child_inst.inherits.params.param_list) == 0
                ):
                    child_inst.params.param_list = (
                        father_instance.params.param_list.copy()
                    )
                    new_params = []
                    for i in child_inst.params.param_list:
                        new_params.append(ID(i.name, ""))
                    child_inst.inherits.params.param_list = new_params

        for child in ast.hierarchy_tree[name].children:
            self.trasspass_params_to_children(ast, child, visited)


class TypeInfChk:
    def __init__(self) -> None:
        self.errors = []
        self.on_type = False
        self.on_function = False
        self.current = ""  # desarrollar idea
        self.sb = None

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node: Program):
        for function in node.functions:
            function: FunctionDef
            function.static_type = (
                function.func_id.annotated_type
                if function.func_id.annotated_type != ""
                else "Object"
            )

        self.on_type = True
        for type_str in node.hierarchy_tree["Object"].children:
            if not type_str in ["Number", "String", "Boolean", "Vector"]:
                self.current = type_str
                self.visit(node.global_definitions[type_str])
        self.current = ""
        self.on_type = False
        
        for function in node.functions:
            function: FunctionDef
            func_expect = function.static_type
            self.visit(function)
            if not conforms(node, function.static_type, func_expect):
                self.errors.append(f"Function '{function.func_id.name}' with annotated type '{func_expect}' returns expresion type '{function.static_type} '")

        self.visit(node.global_exp)
        node.static_type = node.global_exp.static_type

    @visitor.when(TypeDef)
    def visit(self, node: TypeDef):
                
        node.static_type = node.id.name
        for param in node.params.param_list:
            param: ID
            param.static_type = param.annotated_type if param.annotated_type != "" else "Object"
        
        if node.inherits:
            self.visit(node.inherits)

        self.on_function = True
        for method in node.functions:
            method: FunctionDef
            method.static_type = (
                method.func_id.annotated_type
                if method.func_id.annotated_type != ""
                else "Object"
            )
        self.on_function = False

        for assign in node.variables:
            assign: Assign
            self.visit(assign)

        self.on_function = True
        for method in node.functions:
            method: FunctionDef
            self.visit(method)
            if node.inherits:
                method_name = method_name_getter(method, True)
                if method_name in node.global_definitions[node.inherits.id.name].variable_scope:
                    if not func_conforms(node, method, node.global_definitions[node.inherits.id.name].variable_scope[method_name]):
                        self.errors.append(f"Method {method_name} at {node.id.name} not conforms to parent method at {node.global_definitions[node.inherits.id.name].id.name}"+cf.add_line_column(method.func_id.name))
        self.on_function = False

        for child in node.hierarchy_tree[node.id.name].children:
            self.current = child
            self.visit(node.global_definitions[child])

    @visitor.when(FunctionCall)
    def visit(self, node: FunctionCall):
        name = method_name_getter(node, False)
        func_def : FunctionDef = None
        if self.on_type and self.on_function:
            if name in node.variable_scope:
                func_def = node.variable_scope[name]
            elif name in node.global_definitions:
                func_def = node.global_definitions[name]
            else:
                self.errors.append(f"Function {name} not defined"+cf.add_line_column(node.func_id.name))
                
        elif name in node.global_definitions:
            func_def = node.global_definitions[name]
        else:
            self.errors.append(
                f"Function '{name}' doesnt exist"
                + cf.add_line_column(node.func_id.name)
            )
            
        if func_def:
            for e_param, r_param in zip(
                func_def.params.param_list, node.params.param_list
            ):
                expect = e_param.static_type
                self.visit(r_param)
                if not conforms(node, r_param.static_type, expect):
                    self.errors.append(
                        f"Function '{node.func_id.name}' param '{e_param.name}' expected '{expect}', but received '{r_param.static_type}'"
                        + cf.add_line_column(node.func_id.name)
                    )
            node.static_type = func_def.static_type

    @visitor.when(FunctionDef)
    def visit(self, node: FunctionDef):
        for param in node.params.param_list:
            param: ID
            param.static_type = (
                param.annotated_type if param.annotated_type != "" else "Object"
            )

        expect = node.static_type
        self.visit(node.body)
        if not conforms(node, node.body.static_type, expect):
            self.errors.append(
                f"Function '{node.func_id.name}' expect return type '{expect}', but its body returns {node.body.static_type}"
                + cf.add_line_column(node.func_id.name)
            )

    @visitor.when(Let)
    def visit(self, node: Let):
        self.visit(node.assign[0])
        self.visit(node.body)
        node.static_type = node.body.static_type

    @visitor.when(ExpressionBlock)
    def visit(self, node: ExpressionBlock):
        for exp in node.exp_list:
            self.visit(exp)
        node.static_type = node.exp_list[-1].static_type

    @visitor.when(If)
    def visit(self, node: If):
        case_types = []
        for case in node.case_list:
            case: Case
            self.visit(case)
            case_types.append(case.static_type)
        node.static_type = LCA(node, *case_types)

    @visitor.when(While)
    def visit(self, node: While):
        condition_expect = "Boolean"
        self.visit(node.condition)
        if not conforms(node, node.condition.static_type, condition_expect):
            self.errors.append(f"Condition of while returned {node.condition.static_type} while expecting {condition_expect}"+cf.add_line_column(node.tk))

        self.visit(node.body)
        node.static_type = node.body.static_type
        
    @visitor.when(Case)
    def visit(self, node: Case):
        condition_expect = "Boolean"
        self.visit(node.condition)
        if not conforms(node, node.condition.static_type, condition_expect):
            self.errors.append(
                f"Expected 'Boolean' at '{node.branch}' but received '{node.condition.static_type}'"
                + cf.add_line_column(node.branch)
            )
        self.visit(node.body)
        node.static_type = node.body.static_type

    @visitor.when(Assign)
    def visit(self, node: Assign):
        expect = None if node.name.annotated_type == "" else node.name.annotated_type
        self.visit(node.value)
        if expect:
            if not conforms(node, node.value.static_type, expect):
                self.errors.append(
                    f"'{node.value.static_type}' not conforms to '{expect}'"
                    + cf.add_line_column(node.name.name)
                )
            if type(node.global_definitions[expect]) is Protocol:
                expect = node.value.static_type
            node.name.static_type = expect
            node.static_type = expect
        else:
            node.name.static_type = node.value.static_type
            node.static_type = node.value.static_type

    @visitor.when(Num)
    def visit(self, node: Num):
        node.static_type = "Number"

    @visitor.when(Pi)
    def visit(self, node: Pi):
        node.static_type = "Number"

    @visitor.when(E)
    def visit(self, node: E):
        node.static_type = "Number"

    @visitor.when(Rand)
    def visit(self, node: Rand):
        node.static_type = "Number"

    @visitor.when(StringLiteral)
    def visit(self, node: StringLiteral):
        node.static_type = "String"

    @visitor.when(TrueLiteral)
    def visit(self, node: TrueLiteral):
        node.static_type = "Boolean"

    @visitor.when(FalseLiteral)
    def visit(self, node: FalseLiteral):
        node.static_type = "Boolean"

    @visitor.when(ID)
    def visit(self, node: ID):
        node.static_type = node.variable_scope[node.name].static_type

    @visitor.when(TypeCall)
    def visit(self, node: TypeCall):
        node.static_type = node.id.name
        type_def: TypeDef = node.global_definitions[node.id.name]
        for e_param, r_param in zip(
        type_def.params.param_list, node.params.param_list
    ):
            expect = e_param.static_type
            self.visit(r_param)
            if not conforms(node, r_param.static_type, expect):
                self.errors.append(
                    f"Function '{node.func_id.name}' param '{e_param.name}' expected '{expect}', but received '{r_param.static_type}'"
                    + cf.add_line_column(node.func_id.name)
                )

    @visitor.when(UnaryOp)
    def visit(self, node: UnaryOp):
        self.visit(node.operand)
        expect = "Boolean" if node.op == "!" else "Number"
        if not conforms(node, node.operand.static_type, expect):
            self.errors.append(
                f"Unary Operation '{node.op}' expected '{expect}' but received '{node.operand.static_type}'"
                + cf.add_line_column(node.op)
            )
        node.static_type = node.operand.static_type

    @visitor.when(Print)
    def visit(self, node: Print):
        self.visit(node.value)
        node.static_type = "Object"

    @visitor.when(Exp)
    def visit(self, node: Exp):
        expect = "Number"
        self.visit(node.value)
        if not conforms(node, node.value.static_type, expect):
            self.errors.append(
                f"EXP operation expect 'Number' argument, but received '{node.value.static_type}'"
            )
        node.static_type = "Number"

    @visitor.when(Sqrt)
    def visit(self, node: Sqrt):
        expect = "Number"
        self.visit(node.value)
        if not conforms(node, node.value.static_type, expect):
            self.errors.append(
                f"SQRT operation expect 'Number' argument, but received '{node.value.static_type}'"
            )
        node.static_type = "Number"

    @visitor.when(Sin)
    def visit(self, node: Sin):
        expect = "Number"
        self.visit(node.value)
        if not conforms(node, node.value.static_type, expect):
            self.errors.append(
                f"SIN operation expect 'Number' argument, but received '{node.value.static_type}'"
            )
        node.static_type = "Number"

    @visitor.when(Cos)
    def visit(self, node: Cos):
        expect = "Number"
        self.visit(node.value)
        if not conforms(node, node.value.static_type, expect):
            self.errors.append(
                f"COS operation expect 'Number' argument, but received '{node.value.static_type}'"
            )
        node.static_type = "Number"

    @visitor.when(Log)
    def visit(self, node: Log):
        expect = "Number"
        self.visit(node.base)
        self.visit(node.value)
        if not (
            conforms(node, node.value.static_type, expect)
            and conforms(node, node.base.static_type, expect)
        ):
            self.errors.append(
                f"LOG operation expect 'Number' arguments, but received '{node.value.static_type}' and '{node.base.static_type}'"
            )
        node.static_type = "Number"

    @visitor.when(VectorExt)
    def visit(self, node: VectorExt):
        typs = []
        for item in node.items.param_list:
            self.visit(item)
            typs.append(item.static_type)

        # [[[1]],[[2]],[[4]]]
        static_type_internal = LCA(node, *typs)
        node.static_type = StringToken("Vector")
        node.static_type.T = static_type_internal

    @visitor.when(BinOp)
    def visit(self, node: BinOp):
        if node.op not in ["AD", ".", "is", "as"]:

            if node.op in [
                "+",
                "-",
                "*",
                "/",
                "%",
                "^",
                "**",
            ]:
                expect = ("Number", "Number")
                expect_return = "Number"
            elif node.op in ["|", "&"]:
                expect = ("Boolean", "Boolean")
                expect_return = "Boolean"
            elif node.op in [">", "<", ">=", "<=", "==", "!="]:
                expect = ("Number", "Number")
                expect_return = "Boolean"
            else:
                expect = ("Object", "Object")
                expect_return = "String"

            self.visit(node.left)
            self.visit(node.right)

            if not (
                conforms(node, node.left.static_type, expect[0])
                and conforms(node, node.right.static_type, expect[1])
            ):
                self.errors.append(
                    f"Binary operation '{node.op}' expected '{expect}' and received '('{node.left.static_type}', '{node.right.static_type}')'"
                    + cf.add_line_column(node.op)
                )
            node.static_type = expect_return

        elif node.op in ["as", "is"]:
            self.visit(node.left)
            expect = node.right.name
            if not conforms(
                node, node.left.static_type, expect
            ) and expect not in get_descendancy_set(node, node.left.static_type, set()):
                self.errors.append(
                    f"Do not even try to cast '{node.left.static_type}' to '{expect}'"
                    + cf.add_line_column(node.op)
                )
            if node.op == "is":
                expect = "Boolean"
            if type(node.global_definitions[expect]) is Protocol:
                expect = node.left.static_type
            node.static_type = expect

        elif node.op == "AD":
            self.visit(node.left)
            expect = node.left.static_type
            self.visit(node.right)
            if not conforms(node, node.right.static_type, expect):
                self.errors.append(
                    f"Cannot ':=' '{node.right.static_type}' to item with type '{expect}'"
                    + cf.add_line_column(node.op)
                )

            node.static_type = expect

        elif node.op == ".":
            self.visit(node.left)
            context_from = node.left.static_type
            if context_from in set(node.global_definitions).difference(
                set(["Vector", "Number", "Boolean", "String", "Object"])
            ):
                context = node.global_definitions[context_from].variable_scope.copy()
                if type(node.right) is ID:
                    name = node.right.name + "/private"
                    token = name
                else:
                    name = method_name_getter(node.right, True)
                    token = node.right.func_id.name
                if name in context:
                    node.static_type = context[name].static_type
                    if type(node.right) is FunctionCall:
                        function: FunctionDef = context[name]
                        for e_param, r_param in zip(
                            function.params.param_list, node.right.params.param_list
                        ):
                            expect = e_param.static_type
                            self.visit(r_param)
                            if not conforms(node, r_param.static_type, expect):
                                self.errors.append(
                                    f"Function '{node.right.func_id.name}' param '{e_param.name}' expected '{expect}', but received '{r_param.static_type}'"
                                    + cf.add_line_column(node.right.func_id.name)
                                )

                else:
                    self.errors.append(
                        f"Type {context_from} has no member {name}"
                        + cf.add_line_column(token)
                    )
            else:
                try:
                    name = node.right.func_id.name
                except:
                    name = node.right.name
                    
                self.errors.append(
                    f"Cannot obtain member '{name}' from type '{context_from}'"
                    + cf.add_line_column(node.op)
                )


def semantic_check(ast: Program, column_finder):
    cf = column_finder
    errors = []
    scope_visitor = ScopeBuilder()
    scope_visitor.visit(ast)
    errors.extend(scope_visitor.errors)
    if len(errors) == 0:
        type_chk = TypeInfChk()
        type_chk.sb = scope_visitor
        type_chk.visit(ast)
        errors.extend(type_chk.errors)

    # your code here
    return ast, errors


if __name__ == "__main__":
    # code_file = io.open("input/custom_test.hulk").read()
    code_text = """
protocol Iterable {
    next() : Boolean;
    current() : Object;
}
type A () {}
type Elite {
    next() : Boolean => true;
    current() : Elite => new Elite();
}
type L inherits Elite {
    next() : Boolean => true;
    current() : L => new L();
}
let a : Iterable = new Elite() in a.next();
    """
    code_text = """function asd (x,y,z) => print(1);
    type A(x, y, z) {}
    new A(1,2,3);"""
    ast, parsingErrors, _b = hulk_parse(code_text, cf, False)

    print(
        "LEXER FOUND THE FOLLOWING ERRORS:" if len(lexerErrors) > 0 else "LEXING OK!",
        *lexerErrors,
        sep="\n - ",
    )
    print(
        (
            "PARSER FOUND THE FOLLOWING ERRORS:"
            if len(parsingErrors) > 0
            else "PARSING OK!!"
        ),
        *parsingErrors,
        sep="\n - ",
    )
    if ast:
        ast, semantic_check_errors = semantic_check(ast, cf)

        print(
            (
                "SEMANTIC CHECK FOUND THE FOLLOWING ERRORS:"
                if len(semantic_check_errors) > 0
                else "SEMANTIC CHECK OK!!!"
            ),
            *semantic_check_errors,
            sep="\n - ",
        )
        ast: Program
        # create_Hierarchy_graph(ast.hierarchy_tree, "ht")
        # create_Hierarchy_graph(ast.protocol_hierarchy, "ph")
        print("\nGlobal Expression returned:", typeof(ast.global_exp))
        # from hulk_code_gen import CodeGen
        # CodeGen().visit(ast)
        
