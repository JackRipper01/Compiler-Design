from ast import List
from scipy import misc
from hulk_semantic_check import HierarchyNode, ScopeBuilder
from misc import create_AST_graph, get_descendancy_set
import visitor
import misc
from hulk_parser import hulk_parse
from hulk_ast import (
    nodes,
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
        # reordenar node.types para que esten en orden herarquico,tengo node.global_definitions dictionary y node.hierarchy_tree dictionary

        main_def, main_ret = self.visit(node.global_exp)
        with open("./out.c", "w") as f:
            f.write("#include <stdio.h>\n")
            f.write("#include <math.h>\n")
            f.write("#include <stdlib.h>\n")
            f.write("#include <string.h>\n\n")
            f.write("#define tan(x) p_tan(x)")
            f.write(
                """
//Concatenate two strings
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
}
int check_types(char* value, char* type) {
    if (strcmp(value, type) == 0) {
        return 1;
    }
    return 0;
}
typedef struct {
       char *type;
       char* string;   
}Object;
Object* new_Object() {
    Object* obj = (Object*)malloc(sizeof(Object));    
    int string_len = strlen("Object");
    obj->type = (char*)malloc((string_len + 1) * sizeof(char));
    strcpy(obj->type, "Object");

    char memory_address_str[20]; // Assuming a maximum of 20 characters for the address string
    sprintf(memory_address_str, "%p", (void *)obj);
    strcpy(obj->string, concatenate_strings("Object at ", memory_address_str));
    return obj;
}
typedef struct {
    char* type;
    char* string;
    int value;
} BoolObject;
BoolObject* new_BoolObject(int value) {
    BoolObject* obj = (BoolObject*)malloc(sizeof(BoolObject));    
    int string_len = strlen("bool");
    obj->type = (char*)malloc((string_len + 1) * sizeof(char));
    strcpy(obj->type, "bool");

    obj->value = value;

    if (value == 1) {
        obj->string = (char *)malloc((strlen("TRUE")) * sizeof(char));
        strcpy(obj->string, "TRUE");
    } else {
        obj->string = (char *)malloc((strlen("FALSE")) * sizeof(char));
        strcpy(obj->string, "FALSE");
    }
    return obj;
}

typedef struct {
    char* type;
    char* string;
    float value;
} Number;
Number* new_Number(float value) {
    Number* obj = (Number*)malloc(sizeof(Number));    
    int string_len = strlen("Number");
    obj->type = (char*)malloc((string_len + 1) * sizeof(char));
    strcpy(obj->type, "Number");
    
    obj->value = value;
    char buff[32];
    gcvt(value,10,buff);
    int value_len = strlen(buff);
    obj->string = (char *)malloc((10) * sizeof(char));
    strcpy(obj->string, buff);
    return obj;
}

typedef struct {
    char* type;
    char* string;
    char* value;
} StringObject;
StringObject* new_StringObject(char* value) {
    StringObject* obj = (StringObject*)malloc(sizeof(StringObject));    
    int string_len = strlen("string");
    obj->type = (char*)malloc((string_len + 1) * sizeof(char));
    strcpy(obj->type, "string");
    int value_len = strlen(value);
    obj->value = (char*)malloc((value_len + 1) * sizeof(char));
    strcpy(obj->value, value);
    obj->string = (char *)malloc(7 * sizeof(char));
    strcpy(obj->string,obj->value);
    return obj;
}

typedef struct {
    void** data;
    int len;
} VectorExt;\n\n"""
            )
            if node.functions:
                for function in node.functions:
                    f.write(f"{self.visit(function)[0]}\n\n")
            if node.types:
                # ordenando node.types segun la herencia
                list_of_descendients = misc.get_descendancy(node, "Object")
                node_types_reorder = []
                for i in range(len(node.types)):
                    node_types_reorder.append(
                        (node.types[i], list_of_descendients.index(node.types[i].id.name)))
                node_types_reorder.sort(key=lambda x: x[1])
                for i in range(len(node_types_reorder)):
                    node.types[i] = node_types_reorder[i][0]

                for type in node.types:
                    f.write(f"{self.visit(type)[0]}\n\n")

            f.write("int main() {\n\n")
            f.write(f"{main_def}\n\n")
            f.write(f"return {main_ret};\n")
            f.write("return 0;\n")
            f.write("}\n")

    @visitor.when(FunctionDef)
    def visit(self, node):
        node.static_type = "Number*"
        node.ret_point = "ret_point_" + node.func_id.name
        list_params = []
        body_def, body_ret = self.visit(node.body)
        for param in node.params.param_list:
            list_params.append(("Number*", param.name))
        params_c_code = ""
        for param_code in list_params:
            params_c_code += f"{param_code[0]} {param_code[1]},"
        params_c_code = params_c_code[:-1]
        
        
        if node.func_id.name == "tan":
            code = f"""{node.static_type} p_{node.func_id.name}({params_c_code}){{{body_def}
            return {body_ret};
        }}"""
        else:
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
        
        if node.func_id.name == "tan":
            return f"{params_def_code}", f"""p_{node.func_id.name}({params_ret_c_code})"""
        
        return f"{params_def_code}", f"""{node.func_id.name}({params_ret_c_code})"""

    @visitor.when(ExpressionBlock)
    def visit(self, node):
        node.static_type = "Number*"
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
        node.static_type = "Number*"
        assign_def, assign_ret = self.visit(node.assign[0].value)
        var_name = node.assign[0].name.name
        var_type = node.assign[0].name.static_type
        var_type = "Number*"  # temporal
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
        node.static_type = "BoolObject*"
        node.ret_point = "ret_point_if_" + \
            str(node.instance_id)  # analizar id blabla
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
        c_code += f"""if ((int){ret_condition}->value){{
            {def_body}
            return {ret_body};
            }}"""
        return c_code, ""

    @visitor.when(While)
    def visit(self, node):
        node.static_type = "Number*"
        node.ret_point = "ret_point_while_" + str(node.instance_id)
        def_condition, ret_condition = self.visit(node.condition)
        def_body, ret_body = self.visit(node.body)
        c_code = f"""{node.static_type} while_{node.instance_id}(){{
            while(1){{
            int while_body_executed = 0;
            {node.static_type} {node.ret_point} = 0;"""
        c_code += f"{def_condition}"
        c_code += f"""
            if ((int){ret_condition}->value){{
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
        list_func_id_polymorphism = []
        parent_inherited = None
        own_plus_parent_functions = []
        # struct definition
        WWWWTTTTFFFF = "Number*"
        c_code = f"""typedef struct {node.id.name}{{\n"""

        if node.inherits:
            parent_inherited = node.global_definitions[node.inherits.id.name]
            for func in parent_inherited.functions:  # preparando una lista para definir las funciones debajo del struct
                founded_polymorphism = False
                for own_func in node.functions:
                    if own_func.func_id.name == func.func_id.name:
                        own_plus_parent_functions.append(own_func)
                        list_func_id_polymorphism.append(own_func.func_id.name)
                        founded_polymorphism = True
                        break
                if founded_polymorphism:
                    founded_polymorphism = False
                    continue
                # luego del for estaran todas las funciones del padre pero con el polimorfismo aplicado
                own_plus_parent_functions.append(func)

            for var in parent_inherited.variables:  # definiendo variables del padre en el struct
                c_code += f"{WWWWTTTTFFFF} {var.name.name};\n"

            # declarando las funciones del padre en el struct pero con el polimorfismo aplicado
            for func in own_plus_parent_functions:
                c_code += f"""{WWWWTTTTFFFF} (*{func.func_id.name})(void* self"""
                if func.params.param_list:
                    for function_params in func.params.param_list:
                        c_code += f", {WWWWTTTTFFFF} {function_params.name}"
                c_code += ");\n"

            for var in node.variables:  # definiendo las variables propias en struct
                c_code += f"{WWWWTTTTFFFF} {var.name.name};\n"

            for func in node.functions:  # declarando las funciones propias en struct sin incluir la del polimorfismo ya q ya se incluyo junto a las del padre
                if func.func_id.name in list_func_id_polymorphism:
                    continue
                c_code += f"""{WWWWTTTTFFFF} (*{func.func_id.name})(void* self"""
                if func.params.param_list:
                    for function_params in func.params.param_list:
                        c_code += f", {WWWWTTTTFFFF} {function_params.name}"
                c_code += ");\n"
                # annadiendo las funciones propias sin incluir la del polimorfismo ya q esta incluida en esta lista
                own_plus_parent_functions.append(func)
        else:
            for var in node.variables:
                c_code += f"{WWWWTTTTFFFF} {var.name.name};\n"

            for func in node.functions:
                c_code += f"""{WWWWTTTTFFFF} (*{func.func_id.name})(void* self"""
                if func.params.param_list:
                    for function_params in func.params.param_list:
                        c_code += f", {WWWWTTTTFFFF} {function_params.name}"
                c_code += ");\n"

            own_plus_parent_functions = (
                node.functions
            )  # esto esta correcto ya q si no hay padre own + (parent=0) = own xd,lee el nombre de la lista y entenderas

        # end of struct
        c_code += "\nchar* type;\n"
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
        if node.params.param_list:
            c_code = c_code[:-1]
        c_code += f"""){{"""
        c_code += f"""{node.static_type}* obj = ({node.static_type}*)malloc(sizeof({node.static_type}));\n"""

        parent_variables = []
        if node.inherits:
            parent_variables = parent_inherited.variables

        all_variables = node.variables + parent_variables
        for var in all_variables:
            def_variable_value, ret_variable_value = self.visit(var.value)
            c_code += f"""{def_variable_value}"""
            c_code += f"""obj->{var.name.name} = {ret_variable_value};\n"""

        for func in own_plus_parent_functions:
            c_code += f"""obj->{func.func_id.name} = {node.static_type}_{func.func_id.name};\n"""

        c_code += f"""int string_len = strlen("{node.static_type}");
        obj -> type = (char*)malloc((string_len + 1) * sizeof(char));
        strcpy(obj -> type, "{node.static_type}");"""
        c_code += f"""return obj;"""
        c_code += f"""}}"""
        # adding variables and functions of parent to self for the descendants to have it
        node.variables = all_variables
        node.functions = own_plus_parent_functions
        return c_code, ""

    @visitor.when(TypeCall)
    def visit(self, node: TypeCall):
        params_c_code = ""
        def_call = ""
        for param in node.params.param_list:
            def_param, ret_param = self.visit(param)
            def_call += def_param+"\n"
            params_c_code += f"""{ret_param},"""
        params_c_code = params_c_code[:-1]
        def_call += f"""{node.id.name}* {node.name} = new_{node.id.name}({params_c_code});"""
        ret_call = f"""{node.name}"""
        return def_call, ret_call

    @visitor.when(VectorExt)
    def visit(self, node: VectorExt):
        size_of_vect = len(node.items.param_list)
        # implement this with an array of pointers in C
        def_vect = f"""VectorExt* {node.name}(){{
                VectorExt* vector = (VectorExt*)malloc(sizeof(VectorExt));
                void** points = (void**)malloc({size_of_vect}*sizeof(void*));\n"""
        for i in range(size_of_vect):
            def_item, ret_item = self.visit(node.items.param_list[i])
            def_vect += def_item + "\n"
            def_vect += f"""array_of_points[{i}] = {ret_item};\n"""

        def_vect += f"""vector -> data = points;\n"""
        def_vect += f"vector -> len = {size_of_vect};\n"

        def_vect += f"""return vector;"""
        def_vect += "}\n"
        def_vect += f"""VectorExt* {node.ret_point}_{node.instance_id} = {node.name}();"""
        ret_vect = f"{node.ret_point}_{node.instance_id}"
        return def_vect, ret_vect

    @visitor.when(VectorCall)
    def visit(self, node: VectorCall):
        def_index, ret_index = self.visit(node.index)
        def_call = def_index
        def_call += f"""if ({node.id.name}->len < {ret_index}){{
                printf("Index out of bounds: %d, length: %d\\n", {ret_index}, {node.id.name}->len);
                exit(-1);
                
                }}"""
        return def_call, f"""({node.id.name}->data[(int){ret_index}])"""

    @visitor.when(BinOp)
    def visit(self, node):
        node.static_type = "Number*"
        left_def, left_ret = self.visit(node.left)
        right_def, right_ret = self.visit(node.right)
        node.ret_point = "ret_point_bin_op_" + str(node.instance_id)

        if node.op == ".":
            node.static_type = "Point"
            node.right.static_type = "Number*"
            if isinstance(node.right, FunctionCall):
                inicio = right_ret.index("(")
                fin = right_ret.index(")")
                parametros_actuales = right_ret[inicio+1:fin].strip()
                if parametros_actuales:
                    # Si ya existen parámetros, agregar el nuevo al principio separado por coma
                    nuevos_parametros = left_ret + ", " + parametros_actuales
                else:
                    # Si no existen parámetros, simplemente agregar el nuevo
                    nuevos_parametros = left_ret

                # Reemplazar los parámetros antiguos con los nuevos en el string original
                right_ret = right_ret[:inicio+1] + \
                    nuevos_parametros + right_ret[fin:]
            else:
                raise TypeError(
                    f"Error in bin op {left_ret}.{right_ret},not a FunctionCall")
            return "", f"""(({node.static_type}*){left_ret})->{right_ret}"""

        if node.op == "is":
            def_is = f"""{node.static_type} bin_op_{node.instance_id}(){{\n"""
            def_is += f"""{left_def}\n{right_def}\n"""
            def_is += f"""int result=0;"""
            list_of_desc = get_descendancy_set(node, node.static_type)
            for desc in list_of_desc:
                def_is += f"""if check_types({left_ret}->type,{desc}){{\n result = 1;\nreturn result;\n}}\n"""
            def_is += f"""return result;"""
            code += "\n}\n"
            code += f"{node.static_type} {node.ret_point}->value = bin_op_{node.instance_id}();\n"
            return def_is, f"({node.ret_point})"

        if node.op == "as":
            def_as = f"""{left_def}\n"""
            return def_as, f"({right_ret}*){left_ret}"

        if node.op == "AD":
            code = f"""{left_def}
            {right_def}\n"""
            code += f"{left_ret} = {right_ret};"
            ret_code = f"""{left_ret}"""
            return code, ret_code

        if node.op in ["@", "@@"]:
            node.static_type = "StringObject*"
            constructor_name = node.static_type[:-1]
       
        type_bin_op=""
        if node.op in ["+", "-", "*", "/", "%", "^", "**"]:
            type_bin_op = "float"
        elif node.op in [">", "<", ">=", "<=", "==", "!="]:
            type_bin_op = "int"
        else:
            raise TypeError(f"Unknown operator {node.op}")
        
        code = f"""{type_bin_op} bin_op_{node.instance_id}(){{
        {left_def}
        {right_def}"""
        if node.op in ["+", "-", "*", "/", "%"]:
            code += f"\nreturn (float)({left_ret}->value {node.op} {right_ret}->value);\n"
        elif node.op in [">", "<", ">=", "<=", "==", "!="]:
            code += f"\nreturn (int)({left_ret}->value {node.op} {right_ret}->value);\n"
        elif node.op in ["^", "**"]:
            code += f"\nreturn pow({left_ret}->value, {right_ret}->value);\n"
        else:
            raise TypeError(f"Unknown operator {node.op}")
        code += "\n}\n"
        
        # PPPPPPPPPPPPPPPP IIIIIIIIIIIIIIIIIIIIIII EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
        node.static_type = "Number*"
        constructor_name=node.static_type[:-1]
        code += f"{node.static_type} {node.ret_point} = new_{constructor_name}(bin_op_{node.instance_id}());\n"
        
        return code, node.ret_point
    # region ignore_this

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

    @visitor.when(TrueLiteral)
    def visit(self, node):
        def_bool = f"""BoolObject* {node.name} = new_BoolObject(1);"""
        return def_bool, f"""{node.name}"""

    @visitor.when(FalseLiteral)
    def visit(self, node):
        def_bool = f"""BoolObject* {node.name} = new_BoolObject(0);"""
        return def_bool, f"""{node.name}"""

    @visitor.when(Num)
    def visit(self, node):
        def_num = f"""Number* {node.name} = new_Number((float){str(node.value)});"""
        return def_num, f"{node.name}"

    @visitor.when(StringLiteral)
    def visit(self, node):
        def_string = f"""StringObject* {node.name} = new_StringObject("{node.value}");"""
        return def_string, f'"{node.name}"'

    @visitor.when(Pi)
    def visit(self, node):
        def_num = f"""Number* {node.name} = new_Number((float)M_PI);"""
        return def_num, f"{node.name}"

    @visitor.when(E)
    def visit(self, node):
        def_num = f"""Number* {node.name} = new_Number((float)M_E);"""
        return def_num, f"{node.name}"

    @visitor.when(Print)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "Number*"
        node.ret_point = "ret_point_print_" + str(node.instance_id)
        code = f"""{node.static_type} print_{node.instance_id}() {{
{child_def}\n"""
        # if node.static_type == "bool":
        #     code += f"""if ({child_ret}){{\n"""
        #     code += f"""      printf(%s,"TRUE");\n}}\n"""
        #     code += f"""else {{\n     printf(%s,"FALSE");\n}}\n"""

        # elif node.static_type == "string":
        #     code += f"""printf("%s",{child_ret});\n"""
        # elif node.static_type == "Number*":
        #     code += f"""printf("%f",{child_ret}->value);\n"""
        # else:
        code += f"""printf("%s\\n",{child_ret}->string);\n"""

        code += f"""return {child_ret};
}}"""
        code += f"""{node.static_type} {node.ret_point} = print_{node.instance_id}();
"""
        return code, node.ret_point

    @visitor.when(Sqrt)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "float"
        node.ret_point = "ret_point_sqrt_" + str(node.instance_id)
#         code = f"""{node.static_type} sqrt_{node.instance_id}() {{
# {child_def}
# return sqrt({child_ret});
# }}
# {node.static_type} {node.ret_point} = sqrt_{node.instance_id}();
# """
        code = f"""{child_def}\n{node.static_type} {node.ret_point}->value = sqrt({child_ret}->value);"""
        return code, node.ret_point

    @visitor.when(Sin)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "Number*"
        node.ret_point = "ret_point_sin_" + str(node.instance_id)
#         code = f"""{node.static_type} sin_{node.instance_id}() {{
# {child_def}
# return sin({child_ret});
# }}
# {node.static_type} {node.ret_point} = sin_{node.instance_id}();
# """   
        code = f"""{child_def}\n{node.static_type} {node.ret_point} = new_Number(sin({child_ret}->value));"""
        # code = f"""{child_def}\n{node.static_type} {node.ret_point}->value = sin({child_ret}->value);"""
        return code, node.ret_point

    @visitor.when(Cos)
    def visit(self, node):
        child_def, child_ret = self.visit(node.value)
        node.static_type = "Number*"
        node.ret_point = "ret_point_cos_" + str(node.instance_id)
#         code = f"""{node.static_type} cos_{node.instance_id}() {{
# {child_def}
# return cos({child_ret});
# }}
# {node.static_type} {node.ret_point} = cos_{node.instance_id}();
# """   
        code = f"""{child_def}\n{node.static_type} {node.ret_point} = new_Number(cos({child_ret}->value));"""
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


# endregion
if __name__ == "__main__":
    code = """

function sum(x,y) => x + y; 
function concat(x,y) => x@y@" Candelozki";
let a=4 in a+4+5+6;


"""
    import hulk_semantic_check
    ast, error_list, b = hulk_parse(code)
    print(code)
    print(error_list)
    create_AST_graph(nodes, "AST")
    hulk_semantic_check.semantic_check(ast)
    CodeGen().visit(ast)
# let x = true in print(x@" Candelozki");
# type Point3D(x, y, z) inherits Point(x, y){
#     z = z

#     getZ() = > self.z

#     setZ(z) = > self.z := z
#     asd() = > self.x*self.x
# }
# type Point(x, y) {
#     x = x
#     y = y

#     getX() = > self.x
#     getY() = > self.y
#     asd() = > self.x+self.y
#     setX(x) = > self.x := x
#     setY(y) = > self.y := y
# }

# type Point5D(x, y, z, a, b) inherits Point3D(x, y, z){
#     a = a
#     b = b

#     getA() = > self.a
#     getB() = > self.b

#     setA(a) = > self.a := a
#     setB(b) = > self.b := b
# }
