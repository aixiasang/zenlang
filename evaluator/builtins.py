"""
Built-in functions for Zen language.
These are functions that are available globally in every Zen program.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict
from object import (
    Object, ObjectType, 
    Integer, String, Boolean, Nil, NIL, TRUE, FALSE,
    Error, Builtin, native_bool_to_boolean_object
)


def builtin_print(*args: Object) -> Object:
    """
    Built-in print function.
    Prints all arguments separated by spaces.
    """
    if not args:
        print()
    else:
        output_parts = []
        for arg in args:
            if isinstance(arg, String):
                output_parts.append(arg.value)
            elif isinstance(arg, Integer):
                output_parts.append(str(arg.value))
            elif isinstance(arg, Boolean):
                output_parts.append("true" if arg.value else "false")
            elif isinstance(arg, Nil):
                output_parts.append("nil")
            else:
                output_parts.append(arg.inspect())
        
        print(" ".join(output_parts))
    
    return NIL


def builtin_len(*args: Object) -> Object:
    """
    Built-in len function.
    Returns the length of strings.
    """
    if len(args) != 1:
        return Error(f"Wrong number of arguments to len(): expected 1, got {len(args)}")
    
    arg = args[0]
    if isinstance(arg, String):
        return Integer(len(arg.value))
    else:
        return Error(f"len() not supported for {arg.type()}")


def builtin_type(*args: Object) -> Object:
    """
    Built-in type function.
    Returns the type name of an object.
    """
    if len(args) != 1:
        return Error(f"Wrong number of arguments to type(): expected 1, got {len(args)}")
    
    arg = args[0]
    return String(arg.type().lower())


def builtin_str(*args: Object) -> Object:
    """
    Built-in str function.
    Converts objects to string representation.
    """
    if len(args) != 1:
        return Error(f"Wrong number of arguments to str(): expected 1, got {len(args)}")
    
    arg = args[0]
    if isinstance(arg, String):
        return arg  # Already a string
    elif isinstance(arg, Integer):
        return String(str(arg.value))
    elif isinstance(arg, Boolean):
        return String("true" if arg.value else "false")
    elif isinstance(arg, Nil):
        return String("nil")
    else:
        return String(arg.inspect())


def builtin_int(*args: Object) -> Object:
    """
    Built-in int function.
    Converts strings and other types to integers.
    """
    if len(args) != 1:
        return Error(f"Wrong number of arguments to int(): expected 1, got {len(args)}")
    
    arg = args[0]
    if isinstance(arg, Integer):
        return arg  # Already an integer
    elif isinstance(arg, String):
        try:
            return Integer(int(arg.value))
        except ValueError:
            return Error(f"Cannot convert '{arg.value}' to integer")
    elif isinstance(arg, Boolean):
        return Integer(1 if arg.value else 0)
    else:
        return Error(f"Cannot convert {arg.type()} to integer")


def builtin_bool(*args: Object) -> Object:
    """
    Built-in bool function.
    Converts objects to boolean values.
    """
    if len(args) != 1:
        return Error(f"Wrong number of arguments to bool(): expected 1, got {len(args)}")
    
    arg = args[0]
    return native_bool_to_boolean_object(arg.is_truthy())


def builtin_input(*args: Object) -> Object:
    """
    Built-in input function.
    Reads a line from standard input.
    """
    if len(args) > 1:
        return Error(f"Wrong number of arguments to input(): expected 0 or 1, got {len(args)}")
    
    # Optional prompt
    prompt = ""
    if len(args) == 1:
        if isinstance(args[0], String):
            prompt = args[0].value
        else:
            prompt = args[0].inspect()
    
    try:
        result = input(prompt)
        return String(result)
    except EOFError:
        return String("")
    except KeyboardInterrupt:
        return Error("Input interrupted")


def builtin_exit(*args: Object) -> Object:
    """
    Built-in exit function.
    Exits the program with optional exit code.
    """
    if len(args) > 1:
        return Error(f"Wrong number of arguments to exit(): expected 0 or 1, got {len(args)}")
    
    exit_code = 0
    if len(args) == 1:
        if isinstance(args[0], Integer):
            exit_code = args[0].value
        else:
            return Error("Exit code must be an integer")
    
    sys.exit(exit_code)


def builtin_range(*args: Object) -> Object:
    """
    Built-in range function.
    Returns a list of integers (for future list support).
    For now, just return error since we don't have lists yet.
    """
    return Error("range() function requires list support (not yet implemented)")


# Registry of all built-in functions
BUILTINS: Dict[str, Builtin] = {
    "print": Builtin(builtin_print, "print"),
    "len": Builtin(builtin_len, "len"),
    "type": Builtin(builtin_type, "type"),
    "str": Builtin(builtin_str, "str"),
    "int": Builtin(builtin_int, "int"),
    "bool": Builtin(builtin_bool, "bool"),
    "input": Builtin(builtin_input, "input"),
    "exit": Builtin(builtin_exit, "exit"),
    # "range": Builtin(builtin_range, "range"),  # Commented out for now
} 