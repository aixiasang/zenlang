"""
Evaluator for Zen language.
Walks the AST and evaluates expressions and statements.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List, Any, Dict
from zen_ast import *
from object import (
    Object, Environment, ObjectType,
    Integer, String, Boolean, Nil, NIL, TRUE, FALSE,
    ReturnValue, Error, Function, Class, Instance, 
    Builtin, Module, ModuleManager, module_manager,
    native_bool_to_boolean_object,
    is_error, is_return_value
)
from .builtins import BUILTINS


class Evaluator:
    """Main evaluator for Zen language."""
    
    def __init__(self):
        """Initialize evaluator."""
        self.globals = Environment()
        self.current_package = ""  # Current package name
        self.current_file_path = ""  # Current file being evaluated
        self._setup_builtins()
    
    def _setup_builtins(self):
        """Setup built-in functions in global environment."""
        for name, builtin_fn in BUILTINS.items():
            self.globals.set(name, builtin_fn)
    
    def eval(self, node: Node, env: Environment) -> Object:
        """
        Evaluate an AST node.
        
        Args:
            node: AST node to evaluate
            env: Current environment
            
        Returns:
            Evaluated object
        """
        return eval_node(node, env)
    
    def eval_file(self, file_path: str) -> Object:
        """
        Evaluate a Zen file.
        
        Args:
            file_path: Path to the Zen file
            
        Returns:
            Evaluated result
        """
        old_file_path = self.current_file_path
        self.current_file_path = file_path
        
        try:
            return self._load_and_eval_file(file_path)
        finally:
            self.current_file_path = old_file_path
    
    def _load_and_eval_file(self, file_path: str) -> Object:
        """Load and evaluate a file."""
        from lexer import Lexer
        from parser import Parser
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse the file
            lexer = Lexer(source)
            parser = Parser(lexer)
            program = parser.parse_program()
            
            if parser.errors:
                errors = "; ".join(parser.errors)
                return Error(f"Parse errors in {file_path}: {errors}")
            
            # Create module environment
            env = Environment()
            
            # Copy builtins
            for name, builtin in self.globals.items():
                env.set(name, builtin)
            
            # Evaluate the program
            result = eval_node(program, env)
            
            if is_error(result):
                return result
            
            return env  # Return the environment as the module's namespace
            
        except FileNotFoundError:
            return Error(f"Module file not found: {file_path}")
        except Exception as e:
            return Error(f"Error loading module {file_path}: {str(e)}")


def eval_node(node: Node, env: Environment) -> Object:
    """
    Evaluate any AST node.
    
    This is the main dispatch function that calls appropriate
    evaluation functions based on node type.
    """
    # Handle None nodes
    if node is None:
        return NIL
    
    # Program and statements
    if isinstance(node, Program):
        return eval_program(node.statements, env)
    elif isinstance(node, BlockStatement):
        return eval_block_statement(node.statements, env)
    elif isinstance(node, ExpressionStatement):
        return eval_node(node.expression, env)
    elif isinstance(node, ReturnStatement):
        return eval_return_statement(node, env)
    elif isinstance(node, AssignStatement):
        return eval_assign_statement(node, env)
    elif isinstance(node, PackageStatement):
        return eval_package_statement(node, env)
    elif isinstance(node, LoadStatement):
        return eval_load_statement(node, env)
    elif isinstance(node, FunctionStatement):
        return eval_function_statement(node, env)
    elif isinstance(node, ClassStatement):
        return eval_class_statement(node, env)
    
    # Expressions
    elif isinstance(node, IntegerLiteral):
        return Integer(node.value)
    elif isinstance(node, StringLiteral):
        return String(node.value)
    elif isinstance(node, BooleanLiteral):
        return native_bool_to_boolean_object(node.value)
    elif isinstance(node, NilLiteral):
        return NIL
    elif isinstance(node, SelfExpression):
        return eval_self_expression(node, env)
    elif isinstance(node, Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, PrefixExpression):
        return eval_prefix_expression(node, env)
    elif isinstance(node, InfixExpression):
        return eval_infix_expression(node, env)
    elif isinstance(node, CallExpression):
        return eval_call_expression(node, env)
    elif isinstance(node, MemberAccessExpression):
        return eval_member_access_expression(node, env)
    
    else:
        return Error(f"Unknown node type: {type(node)}")


def eval_program(statements: List[Statement], env: Environment) -> Object:
    """Evaluate a program (list of statements)."""
    result = NIL
    
    for statement in statements:
        result = eval_node(statement, env)
        
        # Handle return values and errors
        if isinstance(result, ReturnValue):
            return result.value
        elif isinstance(result, Error):
            return result
    
    return result


def eval_block_statement(statements: List[Statement], env: Environment) -> Object:
    """Evaluate a block of statements."""
    result = NIL
    
    for statement in statements:
        result = eval_node(statement, env)
        
        # Propagate return values and errors up
        if isinstance(result, (ReturnValue, Error)):
            return result
    
    return result


def eval_return_statement(node: ReturnStatement, env: Environment) -> Object:
    """Evaluate return statement."""
    if node.value:
        val = eval_node(node.value, env)
        if is_error(val):
            return val
        return ReturnValue(val)
    else:
        return ReturnValue(NIL)


def eval_assign_statement(node: AssignStatement, env: Environment) -> Object:
    """Evaluate assignment statement."""
    value = eval_node(node.value, env)
    if is_error(value):
        return value
    
    # Handle different assignment targets
    if isinstance(node.target, Identifier):
        # Simple variable assignment: a = 5
        env.set(node.target.value, value)
        return value
    elif isinstance(node.target, MemberAccessExpression):
        # Member assignment: obj.field = value
        return eval_member_assignment(node.target, value, env)
    else:
        return Error(f"Invalid assignment target: {type(node.target)}")


def eval_member_assignment(member_expr: MemberAccessExpression, value: Object, env: Environment) -> Object:
    """Evaluate member assignment (obj.field = value)."""
    obj = eval_node(member_expr.object, env)
    if is_error(obj):
        return obj
    
    if isinstance(obj, Instance):
        obj.set_field(member_expr.member, value)
        return value
    else:
        return Error(f"Cannot assign to member of {obj.type()}")


def eval_package_statement(node: PackageStatement, env: Environment) -> Object:
    """Evaluate package statement."""
    # Store package name for visibility checking
    package_name = node.name
    env.set("__package__", String(package_name))
    return NIL


def eval_load_statement(node: LoadStatement, env: Environment) -> Object:
    """Evaluate load statement."""
    result = NIL
    
    for module_path in node.imports:
        module_result = load_module(module_path, env)
        if is_error(module_result):
            return module_result
        result = module_result
    
    return result


def load_module(module_path: str, env: Environment) -> Object:
    """
    Load a module and make it available in the current environment.
    
    Args:
        module_path: Path to the module (e.g., "math", "utils/helpers")
        env: Current environment
        
    Returns:
        Module object or Error
    """
    # Check if module is already cached
    cached_module = module_manager.get_cached_module(module_path)
    if cached_module:
        # Module already loaded, add to environment
        module_name = extract_module_name(module_path)
        env.set(module_name, cached_module)
        return cached_module
    
    # Check for circular imports
    if module_manager.is_loading(module_path):
        return Error(f"Circular import detected: {module_path}")
    
    # Resolve the module path to an actual file
    current_dir = os.getcwd()
    file_path = module_manager.resolve_module_path(module_path, current_dir)
    
    if not file_path:
        return Error(f"Module not found: {module_path}")
    
    # Mark as loading
    module_manager.start_loading(module_path)
    
    try:
        # Load and parse the file
        from lexer import Lexer
        from parser import Parser
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            errors = "; ".join(parser.errors)
            return Error(f"Parse errors in {module_path}: {errors}")
        
        # Create module environment
        module_env = Environment()
        
        # Copy builtins to module environment
        evaluator = Evaluator()
        for name, builtin in evaluator.globals.items():
            module_env.set(name, builtin)
        
        # Evaluate the module
        result = eval_node(program, module_env)
        
        if is_error(result):
            return result
        
        # Extract package name if declared
        package_obj = module_env.get("__package__")
        package_name = package_obj.value if isinstance(package_obj, String) else ""
        
        # Create public environment (only uppercase names)
        public_env = Environment()
        for name, obj in module_env.items():
            if is_public_name(name):
                public_env.set(name, obj)
        
        # Create module object
        module = Module(
            name=extract_module_name(module_path),
            path=file_path,
            env=public_env,
            private_env=module_env,
            package_name=package_name
        )
        
        # Cache the module
        module_manager.cache_module(module_path, module)
        
        # Add module to current environment
        module_name = extract_module_name(module_path)
        env.set(module_name, module)
        
        return module
        
    except FileNotFoundError:
        return Error(f"Module file not found: {module_path}")
    except Exception as e:
        return Error(f"Error loading module {module_path}: {str(e)}")
    finally:
        # Mark as finished loading
        module_manager.finish_loading(module_path)


def extract_module_name(module_path: str) -> str:
    """Extract module name from path."""
    # Remove .zen extension if present
    if module_path.endswith('.zen'):
        module_path = module_path[:-4]
    
    # Get the last part of the path
    parts = module_path.replace('\\', '/').split('/')
    return parts[-1]


def is_public_name(name: str) -> bool:
    """Check if a name is public (Zen visibility rules)."""
    # Skip internal names
    if name.startswith('__'):
        return False
    
    # Public names start with uppercase letter
    return name and name[0].isupper()


def eval_function_statement(node: FunctionStatement, env: Environment) -> Object:
    """Evaluate function statement."""
    function = Function(
        parameters=node.parameters,
        body=node.body,
        env=env,  # Capture current environment for closure
        name=node.name
    )
    env.set(node.name, function)
    return function


def eval_class_statement(node: ClassStatement, env: Environment) -> Object:
    """Evaluate class statement."""
    methods = {}
    
    # Evaluate each method
    for method_node in node.methods:
        method_func = Function(
            parameters=method_node.parameters,
            body=method_node.body,
            env=env,
            name=method_node.name
        )
        methods[method_node.name] = method_func
    
    cls = Class(name=node.name, methods=methods)
    env.set(node.name, cls)
    return cls


def eval_self_expression(node: SelfExpression, env: Environment) -> Object:
    """Evaluate self expression."""
    self_obj = env.get("self")
    if self_obj is None:
        return Error("'self' used outside of instance method")
    return self_obj


def eval_identifier(node: Identifier, env: Environment) -> Object:
    """Evaluate identifier."""
    val = env.get(node.value)
    if val is None:
        return Error(f"Identifier not found: {node.value}")
    return val


def eval_prefix_expression(node: PrefixExpression, env: Environment) -> Object:
    """Evaluate prefix expression."""
    right = eval_node(node.right, env)
    if is_error(right):
        return right
    
    return apply_prefix_operator(node.operator, right)


def apply_prefix_operator(operator: str, right: Object) -> Object:
    """Apply prefix operator to operand."""
    if operator == "!":
        return apply_bang_operator(right)
    elif operator == "-":
        return apply_minus_operator(right)
    else:
        return Error(f"Unknown prefix operator: {operator}")


def apply_bang_operator(operand: Object) -> Object:
    """Apply logical NOT operator."""
    if operand is TRUE:
        return FALSE
    elif operand is FALSE:
        return TRUE
    elif operand is NIL:
        return TRUE
    else:
        return FALSE


def apply_minus_operator(operand: Object) -> Object:
    """Apply unary minus operator."""
    if isinstance(operand, Integer):
        return Integer(-operand.value)
    else:
        return Error(f"Unknown operator: -{operand.type()}")


def eval_infix_expression(node: InfixExpression, env: Environment) -> Object:
    """Evaluate infix expression."""
    left = eval_node(node.left, env)
    if is_error(left):
        return left
    
    right = eval_node(node.right, env)
    if is_error(right):
        return right
    
    return apply_infix_operator(node.operator, left, right)


def apply_infix_operator(operator: str, left: Object, right: Object) -> Object:
    """Apply infix operator to operands."""
    # Integer operations
    if isinstance(left, Integer) and isinstance(right, Integer):
        return apply_integer_infix_operator(operator, left, right)
    
    # String operations
    elif isinstance(left, String) and isinstance(right, String):
        return apply_string_infix_operator(operator, left, right)
    
    # Boolean operations
    elif operator in ["==", "!="]:
        return apply_equality_operator(operator, left, right)
    
    # Logical operations
    elif operator in ["&&", "||"]:
        return apply_logical_operator(operator, left, right)
    
    else:
        return Error(f"Unknown operator: {left.type()} {operator} {right.type()}")


def apply_integer_infix_operator(operator: str, left: Integer, right: Integer) -> Object:
    """Apply infix operator to integers."""
    left_val = left.value
    right_val = right.value
    
    if operator == "+":
        return Integer(left_val + right_val)
    elif operator == "-":
        return Integer(left_val - right_val)
    elif operator == "*":
        return Integer(left_val * right_val)
    elif operator == "/":
        if right_val == 0:
            return Error("Division by zero")
        return Integer(left_val // right_val)  # Integer division
    elif operator == "<":
        return native_bool_to_boolean_object(left_val < right_val)
    elif operator == ">":
        return native_bool_to_boolean_object(left_val > right_val)
    elif operator == "<=":
        return native_bool_to_boolean_object(left_val <= right_val)
    elif operator == ">=":
        return native_bool_to_boolean_object(left_val >= right_val)
    elif operator == "==":
        return native_bool_to_boolean_object(left_val == right_val)
    elif operator == "!=":
        return native_bool_to_boolean_object(left_val != right_val)
    else:
        return Error(f"Unknown integer operator: {operator}")


def apply_string_infix_operator(operator: str, left: String, right: String) -> Object:
    """Apply infix operator to strings."""
    if operator == "+":
        return String(left.value + right.value)
    elif operator == "==":
        return native_bool_to_boolean_object(left.value == right.value)
    elif operator == "!=":
        return native_bool_to_boolean_object(left.value != right.value)
    else:
        return Error(f"Unknown string operator: {operator}")


def apply_equality_operator(operator: str, left: Object, right: Object) -> Object:
    """Apply equality operator to any objects."""
    if operator == "==":
        return native_bool_to_boolean_object(objects_equal(left, right))
    elif operator == "!=":
        return native_bool_to_boolean_object(not objects_equal(left, right))
    else:
        return Error(f"Unknown equality operator: {operator}")


def apply_logical_operator(operator: str, left: Object, right: Object) -> Object:
    """Apply logical operator."""
    if operator == "&&":
        if not left.is_truthy():
            return left
        return right
    elif operator == "||":
        if left.is_truthy():
            return left
        return right
    else:
        return Error(f"Unknown logical operator: {operator}")


def objects_equal(left: Object, right: Object) -> bool:
    """Check if two objects are equal."""
    if left.type() != right.type():
        return False
    
    if isinstance(left, Integer) and isinstance(right, Integer):
        return left.value == right.value
    elif isinstance(left, String) and isinstance(right, String):
        return left.value == right.value
    elif isinstance(left, Boolean) and isinstance(right, Boolean):
        return left.value == right.value
    elif left is NIL and right is NIL:
        return True
    else:
        return left is right  # Reference equality for other objects


def eval_call_expression(node: CallExpression, env: Environment) -> Object:
    """Evaluate function call expression."""
    function = eval_node(node.function, env)
    if is_error(function):
        return function
    
    # Evaluate arguments
    args = []
    for arg_node in node.arguments:
        arg = eval_node(arg_node, env)
        if is_error(arg):
            return arg
        args.append(arg)
    
    return apply_function(function, args, env)


def apply_function(fn: Object, args: List[Object], env: Environment) -> Object:
    """Apply function to arguments."""
    if isinstance(fn, Function):
        return apply_user_function(fn, args)
    elif isinstance(fn, Builtin):
        return fn.fn(*args)
    elif isinstance(fn, Class):
        return apply_class_constructor(fn, args)
    else:
        return Error(f"Not a function: {fn.type()}")


def apply_user_function(fn: Function, args: List[Object]) -> Object:
    """Apply user-defined function."""
    # Check parameter count
    if len(args) != len(fn.parameters):
        return Error(f"Wrong number of arguments: expected {len(fn.parameters)}, got {len(args)}")
    
    # Create new environment for function execution
    extended_env = fn.env.new_enclosed_environment()
    
    # Bind parameters to arguments
    for param, arg in zip(fn.parameters, args):
        extended_env.set(param, arg)
    
    # Execute function body
    evaluated = eval_node(fn.body, extended_env)
    
    # Unwrap return values
    if isinstance(evaluated, ReturnValue):
        return evaluated.value
    else:
        return evaluated


def apply_class_constructor(cls: Class, args: List[Object]) -> Object:
    """Apply class constructor (instantiate class)."""
    # Create new instance
    instance = Instance(cls=cls, fields=Environment())
    
    # Check for __init__ method
    init_method = cls.get_method("__init__")
    if init_method:
        # Call __init__ with self as first argument
        init_args = [instance] + args
        result = apply_user_function(init_method, init_args)
        if is_error(result):
            return result
    
    return instance


def eval_member_access_expression(node: MemberAccessExpression, env: Environment) -> Object:
    """Evaluate member access expression."""
    obj = eval_node(node.object, env)
    if is_error(obj):
        return obj
    
    if isinstance(obj, Instance):
        # First try instance fields
        field = obj.get_field(node.member)
        if field is not None:
            return field
        
        # Then try methods
        method = obj.get_method(node.member)
        if method is not None:
            # Return bound method (method with self pre-bound)
            return create_bound_method(method, obj)
        
        return Error(f"Attribute '{node.member}' not found on {obj.cls.name} instance")
    
    elif isinstance(obj, Module):
        # Module member access
        member = obj.get_member(node.member)
        if member is not None:
            return member
        return Error(f"Module '{obj.name}' has no public attribute '{node.member}'")
    
    elif isinstance(obj, Class):
        method = obj.get_method(node.member)
        if method is not None:
            return method
        return Error(f"Class '{obj.name}' has no attribute '{node.member}'")
    
    else:
        return Error(f"Cannot access member '{node.member}' on {obj.type()}")


def create_bound_method(method: Function, instance: Object) -> Function:
    """Create a bound method with self pre-bound."""
    # Create new environment with self bound
    bound_env = method.env.new_enclosed_environment()
    bound_env.set("self", instance)
    
    # Create new function with bound environment
    return Function(
        parameters=method.parameters[1:] if method.parameters and method.parameters[0] == "self" else method.parameters,
        body=method.body,
        env=bound_env,
        name=method.name
    ) 