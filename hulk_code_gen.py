from hulk_semantic_check import ScopeBuilder
from misc import create_AST_graph
import visitor

from hulk_parser import hulk_parse
from hulk_ast import (nodes,
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


class CodeGen:
    def __init__(self):
        self.errors = []
        self.global_definitions = {}

    @visitor.on("node")
    def visit(self, node):
        pass

    @visitor.when(Program)
    def visit(self, node):
        main_def, main_ret = self.visit(node.global_exp)
        with open("./out.c", "w") as f:
            f.write("#include <stdio.h>\n")
            f.write("#include <math.h>\n")
            f.write("#include <stdlib.h>\n")
            f.write("#include <string.h>\n\n")
            f.write(
                """//Concatenate two strings
        char* concatenate_strings(const char* str1, const char* str2) {
        // Calculate the length needed for the concatenated string
        int length = strlen(str1) + strlen(str2) + 1; // +1 for the null terminator

        // Allocate memory for the concatenated string
        char* result = (char*)malloc(length * sizeof(char));
        if (result == NULL) {
            printf("Memory allocation failed");
            exit(1); // Exit if memory allocation fails
        }

        // Copy the first string and concatenate the second string
        strcpy(result, str1);
        strcat(result, str2);

        return result;
    }\n\n"""
            )
            if node.functions:
                for function in node.functions:
                    f.write(f"{self.visit(function)[0]}\n\n")
            if node.types:
                for type in node.types:
                    f.write(f"{self.visit(type)[0]}\n\n")  # revisar si pincho
            f.write("float main() {\n\n")
            f.write(f"{main_def}\n\n")
            f.write(f"return {main_ret};\n")
            f.write("}\n")

    @visitor.when(FunctionDef)
    def visit(self, node):
        node.static_type = "float"
        node.ret_point = "ret_point_" + node.func_id.name
        list_params = []
        body_def, body_ret = self.visit(node.body)
        for param in node.params.param_list:
            list_params.append(("float", param.name))
        params_c_code = ""
        for param_code in list_params:
            params_c_code += f"{param_code[0]} {param_code[1]},"
        params_c_code = params_c_code[:-1]
        code = f"""{node.static_type} {node.func_id.name}({params_c_code}){{{body_def}
        return {body_ret};
        }}"""

        params_name_c_code = ""
        for param_name in list_params:
            params_name_c_code += param_name[1] + ","
        params_name_c_code = params_name_c_code[:-1]
        ret_code = f"""{node.func_id.name}({params_name_c_code})"""

        return code, ret_code

    @visitor.when(FunctionCall)
    def visit(self, node):
        def_ret_list_params = []
        for param in node.params.param_list:
            construct_params = self.visit(param)
            def_ret_list_params.append(construct_params)

        params_def_code = ""
        for param_def_code in def_ret_list_params:
            if param_def_code[0] != "":
                params_def_code += param_def_code[0] + "\n"

        params_ret_c_code = ""
        for param_ret_code in def_ret_list_params:
            params_ret_c_code += param_ret_code[1] + ","

        params_ret_c_code = params_ret_c_code[:-1]
        return f"{params_def_code}", f"""{node.func_id.name}({params_ret_c_code})"""

    @visitor.when(ExpressionBlock)
    def visit(self, node):
        node.static_type = "float"
        node.ret_point = "ret_point_expression_block_" + str(
            node.instance_id
        )  # analizar lo del id pa q no haya lio
        code = f"""{node.static_type} {node.name}() {{
        """
        for exp, i in zip(node.exp_list, range(len(node.exp_list))):
            body_def, body_ret = self.visit(exp)
            code += body_def + "\n"
            if i == len(node.exp_list) - 1:
                code += f"return {body_ret};\n"
        code += "}"
        code += f"""{node.static_type} {node.ret_point} = expression_block_{node.instance_id}();"""
        return code, node.ret_point

    @visitor.when(Let)
    def visit(self, node):
        node.static_type = "float"
        assign_def, assign_ret = self.visit(node.assign[0].value)
        var_name = node.assign[0].name.name
        var_type = node.assign[0].name.static_type
        var_type = "float"  # temporal
        body_def, body_ret = self.visit(node.body)
        node.ret_point = "ret_point_let_" + str(
            node.instance_id
        )  # analizar instance id

        c_code = f"""{node.static_type} let_{node.instance_id}(){{
        {assign_def}
        {var_type} {var_name} = {assign_ret};
        {body_def}
        return {body_ret};
        }}
        {node.static_type} {node.ret_point} = let_{node.instance_id}();
        """
        return c_code, node.ret_point

    @visitor.when(ID)
    def visit(self, node):
        return "", node.name

    @visitor.when(If)
    def visit(self, node):
        node.static_type = "float"
        node.ret_point = "ret_point_if_" + str(node.instance_id)  # analizar id blabla
        c_code = f"""{node.static_type} if_{node.instance_id}(){{"""
        for case in node.case_list:
            def_case, ret_case = self.visit(case)
            c_code += f"{def_case}"
            c_code += "\n"
        c_code += "}\n"
        c_code += f"{node.static_type} {node.ret_point} = if_{node.instance_id}();"
        return c_code, node.ret_point

    @visitor.when(Case)
    def visit(self, node):
        c_code = ""
        def_condition, ret_condition = self.visit(node.condition)
        def_body, ret_body = self.visit(node.body)
        c_code += f"""{def_condition}"""
        c_code += f"""if ((int){ret_condition}){{
            {def_body}
            return {ret_body};
            }}"""
        return c_code, ""

    @visitor.when(While)
    def visit(self, node):
        node.static_type = "float"
        node.ret_point = "ret_point_while_" + str(node.instance_id)
        def_condition, ret_condition = self.visit(node.condition)
        def_body, ret_body = self.visit(node.body)
        c_code = f"""{node.static_type} while_{node.instance_id}(){{
            while(1){{
            int while_body_executed = 0;
            {node.static_type} {node.ret_point} = 0;"""
        c_code += f"{def_condition}"
        c_code += f"""
            if ((int){ret_condition}){{
            while_body_executed = 1;
            {def_body}
            {node.ret_point} = {ret_body};
            }}
            else{{
                if (while_body_executed == 1)
                    return {node.ret_point};
                else
                break;//que carajo retorno
            }}"""
        c_code += "}\n}\n"

        c_code += f"{node.static_type} {node.ret_point} = while_{node.instance_id}();"
        return c_code, node.ret_point

    @visitor.when(TypeDef)
    def visit(self, node):
        node.static_type = node.id.annotated_type
        own_plus_parent_variables = []
        list_func_id_polymorphism = []
        own_plus_parent_functions =[]
        parent_inherited=None

        # struct definition
        WWWWTTTTFFFF = "float"
        c_code = f"""typedef struct {node.id.name}{{\n"""

        if node.inherits:
            parent_inherited = node.global_definitions[node.inherits.id.name]
            c_code += f"""char base[] = "{node.inherits.id.name}";\n"""
            for var in parent_inherited.variables:
                own_plus_parent_variables.append(var)
            for func in parent_inherited.functions:
                founded_polymorphism = False
                for own_func in node.functions:
                    if own_func.func_id.name == func.func_id.name:
                        own_plus_parent_functions.append(own_func)
                        list_func_id_polymorphism.append(own_func.func_id.name)
                        founded_polymorphism=True
                        break
                if founded_polymorphism:
                    founded_polymorphism=False
                    continue
                own_plus_parent_functions.append(func)
            own_plus_parent_functions.extend(node.functions)
        else:
            c_code += """char base[] = "Object";\n"""
            own_plus_parent_variables=node.variables
            own_plus_parent_functions=node.functions

        for var in own_plus_parent_variables:
            c_code += f"{WWWWTTTTFFFF} {var.name.name};\n"
        for func in own_plus_parent_functions:
            if func.func_id.name in list_func_id_polymorphism:
                continue
            c_code += f"""{WWWWTTTTFFFF} (*{func.func_id.name})(void* self"""
            if func.params.param_list:
                for function_params in func.params.param_list:
                    c_code += f", {WWWWTTTTFFFF} {function_params.name}"
            c_code += ");\n"
        c_code += f"}} {node.id.name};\n"

        # functions definition
        for func in own_plus_parent_functions:
            def_func, ret_func = self.visit(func)  
            c_code += f"""{func.static_type} {node.static_type}_{func.func_id.name}(void* self"""
            if func.params.param_list:
                for function_params in func.params.param_list:
                    c_code += f", {WWWWTTTTFFFF} {function_params.name}"
            c_code += f"""){{\n{def_func}\nreturn {ret_func};\n}}\n\n"""

        # constructor definition
        c_code += f"""{node.static_type}* new_{node.static_type}("""
        for param in node.params.param_list:
            c_code += f"{WWWWTTTTFFFF} {param.name},"
        c_code = c_code[:-1]
        c_code += f"""){{"""
        c_code += f"""{node.static_type}* obj = ({node.static_type}*)malloc(sizeof({node.static_type}));\n"""

        for var in own_plus_parent_variables:
            def_variable_value, ret_variable_value = self.visit(var.value)  
            c_code += f"""{def_variable_value}"""
            c_code += f"""obj->{var.name.name} = {ret_variable_value};\n"""

        for func in own_plus_parent_functions:
            c_code += f"""obj->{func.func_id.name} = {node.static_type}_{func.func_id.name};\n"""
        c_code += f"""return obj;"""
        c_code += f"""}}"""
        return c_code, ""

    @visitor.when(TrueLiteral)
    def visit(self, node):
        return "", "1"

    @visitor.when(FalseLiteral)
    def visit(self, node):
        return "", "0"

    @visitor.when(BinOp)
    def visit(self, node):
        node.static_type = "float"
        left_def, left_ret = self.visit(node.left)
        right_def, right_ret = self.visit(node.right)
        node.ret_point = "ret_point_bin_op_" + str(node.instance_id)

        if node.op == ".":
            node.static_type = "Point"
            node.right.static_type = "float"  # ESTO CREEEEEEEEEEEEEEO q VA A DAR ERRORRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR PQ RIGHT>STATICTYPE CREO Q USA SELF>STATICTYPE Y NO NODE>STATIC TYPE
            # code = f"""{node.right.static_type} bin_op_{node.instance_id}(){{"""
            # code += f"return (({node.static_type}*){left_ret})->{right_ret};\n}}"
            # code += f"{node.right.static_type} {node.ret_point} = bin_op_{node.instance_id}();\n"
            return "", f"""(({node.static_type}*){left_ret})->{right_ret}"""

        # if self.op == "AS":
        #     return "", f"({right_ret}*){left_ret}"

        code = f"""{node.static_type} bin_op_{node.instance_id}(){{
        {left_def}
        {right_def}"""
        if node.op in ["+", "-", "*", "/", "%"]:
            code += f"\nreturn (float)({left_ret} {node.op} {right_ret});\n"
        elif node.op in [">", "<", ">=", "<=", "==", "!="]:
            code += f"\nreturn (int)({left_ret} {node.op} {right_ret});\n"
        elif node.op in ["^", "**"]:
            code += f"\nreturn = (pow({left_ret}, {right_ret});\n"
        elif node.op == "AD":
            code += f"return {left_ret} = {right_ret};"
        else:
            raise TypeError(f"Unknown operator {node.op}")
        code += "\n}\n"
        code += f"{node.static_type} {node.ret_point} = bin_op_{node.instance_id}();\n"
        return code, node.ret_point

    @visitor.when(UnaryOp)
    def visit(self, node):
        if node.op == "-":  # recuerda el not
            node.static_type = "float"
            child_def, child_ret = self.visit(node.value)
            node.ret_point = "ret_point_unary_op_" + str(node.instance_id)
            code = f"""{node.static_type} unary_op_{node.instance_id}() {{
{child_def}
return -{child_ret};
}}
{node.static_type} {node.ret_point} = unary_op_{node.instance_id}();
"""
            return code, node.ret_point
        else:
            raise TypeError(f"Unknown unary operator {node.op}")

    @visitor.when(Num)
    def visit(self, node):
        return "", "(float)" + str(node.value)

    @visitor.when(StringLiteral)
    def visit(self, node):
        return "", f'"{node.value}"'

    @visitor.when(Pi)
    def visit(self, node):
        return "", "M_PI"

    @visitor.when(E)
    def visit(self, node):
        return "", "M_E"

    @visitor.when(Print)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_print_" + str(node.instance_id)
        code = f"""{node.static_type} print_{node.instance_id}() {{
{child_def}

printf("%f\\n",{child_ret});
return {child_ret};
}}
{node.static_type} {node.ret_point} = print_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Sqrt)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_sqrt_" + str(node.instance_id)
        code = f"""{node.static_type} sqrt_{node.instance_id}() {{
{child_def}
return sqrt({child_ret});
}}
{node.static_type} {node.ret_point} = sqrt_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Sin)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_sin_" + str(node.instance_id)
        code = f"""{node.static_type} sin_{node.instance_id}() {{
{child_def}
return sin({child_ret});
}}
{node.static_type} {node.ret_point} = sin_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Cos)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_cos_" + str(node.instance_id)
        code = f"""{node.static_type} cos_{node.instance_id}() {{
{child_def}
return cos({child_ret});
}}
{node.static_type} {node.ret_point} = cos_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Exp)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_exp_" + str(node.instance_id)
        code = f"""{node.static_type} exp_{node.instance_id}() {{
{child_def}
return exp({child_ret});
}}
{node.static_type} {node.ret_point} = exp_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Log)
    def visit(self, node):
        child_def_base, child_ret_base = self.visit(node.base)
        child_def_value, child_ret_value = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_log_" + str(node.instance_id)
        code = f"""{node.static_type} log_{node.instance_id}() {{
{child_def_base}
{child_def_value}
return log({child_ret_value})/log({child_ret_base});
}}
{node.static_type} {node.ret_point} = log_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Rand)
    def visit(self, node):
        return "", f"(float)rand()/(float)RAND_MAX"


if __name__ == "__main__":
    ast,a = hulk_parse(
        """type Point(x,y) {
    x = x;
    y = y;

    getX() => self.x;
    getY() => self.y;

    setX(x) => self.x := x;
    setY(y) => self.y := y;
}
type Point3D(x,y,z) inherits Point(x,y){
    z=z;

    getZ() => self.z;

    setZ(z) => self.z := z;
}
4;"""
    )
    create_AST_graph(nodes, "AST")
    ScopeBuilder().get_global_definitions(ast)
    code_gen_instance=CodeGen()
    code_gen_instance.visit(ast)
