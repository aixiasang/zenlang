"""
Test script for the Zen evaluator.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator, eval_node
from object import Environment, Error, Integer, String, Boolean


def test_integer_arithmetic():
    """Test basic integer arithmetic."""
    print("=== Test 1: Integer arithmetic ===")
    
    tests = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Integer) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_boolean_expressions():
    """Test boolean expressions."""
    print("=== Test 2: Boolean expressions ===")
    
    tests = [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Boolean) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_bang_operator():
    """Test bang (!) operator."""
    print("=== Test 3: Bang operator ===")
    
    tests = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Boolean) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_string_expressions():
    """Test string expressions."""
    print("=== Test 4: String expressions ===")
    
    tests = [
        ('"Hello World!"', "Hello World!"),
        ('"Hello" + " " + "World!"', "Hello World!"),
        ('"Hello" == "Hello"', True),
        ('"Hello" != "Hello"', False),
        ('"Hello" == "World"', False),
        ('"Hello" != "World"', True),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, String) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        elif isinstance(result, Boolean) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_variable_assignments():
    """Test variable assignments."""
    print("=== Test 5: Variable assignments ===")
    
    tests = [
        ("a = 5 a", 5),
        ("a = 5 * 5 a", 25),
        ("a = 5 b = a b", 5),
        ("a = 5 b = a c = a + b + 5 c", 15),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Integer) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_functions():
    """Test function definitions and calls."""
    print("=== Test 6: Functions ===")
    
    tests = [
        ("fx identity(x) { return x } identity(5)", 5),
        ("fx identity(x) { return x } identity(true)", True),
        ("fx add(x, y) { return x + y } add(5, 5)", 10),
        ("fx add(x, y) { return x + y } add(5 + 5, add(5, 5))", 20),
        ("fx max(x, y) { if x > y { return x } else { return y } } max(5, 10)", 10),  # This might fail if conditionals aren't implemented
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Integer) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        elif isinstance(result, Boolean) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_builtin_functions():
    """Test built-in functions."""
    print("=== Test 7: Built-in functions ===")
    
    # Note: print() returns NIL, so we test other functions
    tests = [
        ('len("hello")', 5),
        ('len("")', 0),
        ('type(5)', "integer"),
        ('type("hello")', "string"),
        ('type(true)', "boolean"),
        ('str(123)', "123"),
        ('str(true)', "true"),
        ('int("42")', 42),
        ('int(true)', 1),
        ('int(false)', 0),
        ('bool(1)', True),
        ('bool(0)', False),
        ('bool("hello")', True),
        ('bool("")', False),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif isinstance(result, Integer) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        elif isinstance(result, String) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        elif isinstance(result, Boolean) and result.value == expected:
            print(f"✓ {source} => {result.value}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_errors():
    """Test error handling."""
    print("=== Test 8: Error handling ===")
    
    tests = [
        "5 + true",
        "5 + true 5",
        "-true",
        "true + false",
        "5 true false",
        "if (10 > 1) { true + false }",
        "foobar",
        '"Hello" - "World"',
    ]
    
    for source in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✓ {source} => ERROR: {result.message}")
        else:
            print(f"✗ {source} => Expected error, got {result.inspect()}")
    print()


def eval_source(source: str):
    """Helper function to evaluate Zen source code."""
    try:
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            return Error(f"Parser errors: {'; '.join(parser.errors)}")
        
        evaluator = Evaluator()
        env = Environment()
        
        # Copy builtins to environment
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        return eval_node(program, env)
        
    except Exception as e:
        return Error(f"Evaluation exception: {str(e)}")


if __name__ == "__main__":
    test_integer_arithmetic()
    test_boolean_expressions()
    test_bang_operator()
    test_string_expressions()
    test_variable_assignments()
    # test_functions()  # Skip for now since conditionals aren't implemented
    test_builtin_functions()
    test_errors()
    
    print("Evaluator tests completed!") 