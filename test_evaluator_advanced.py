"""
Advanced test script for the Zen evaluator.
Tests functions, classes, and more complex scenarios.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator, eval_node
from object import Environment, Error, Integer, String, Boolean, NIL


def test_basic_functions():
    """Test basic function definitions and calls."""
    print("=== Test 1: Basic Functions ===")
    
    tests = [
        # Simple function
        ("fx identity(x) { return x } identity(5)", 5),
        ("fx identity(x) { return x } identity(true)", True),
        
        # Function with multiple parameters
        ("fx add(x, y) { return x + y } add(5, 5)", 10),
        ("fx add(x, y) { return x + y } add(5 + 5, add(5, 5))", 20),
        
        # Function without explicit return
        ("fx getValue() { 42 } getValue()", 42),
        
        # Nested function calls
        ("fx double(x) { return x * 2 } fx quadruple(x) { return double(double(x)) } quadruple(5)", 20),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif check_result(result, expected):
            print(f"✓ {source} => {get_result_value(result)}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_closures():
    """Test closure functionality."""
    print("=== Test 2: Closures ===")
    
    tests = [
        # Simple closure
        ("""
        fx makeAdder(x) {
            return fx(y) { return x + y }
        }
        addFive = makeAdder(5)
        addFive(10)
        """, 15),
        
        # Counter closure
        ("""
        fx makeCounter() {
            count = 0
            return fx() { 
                count = count + 1
                return count 
            }
        }
        counter = makeCounter()
        counter()
        counter()
        """, 2),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ Closure test => ERROR: {result.inspect()}")
        elif check_result(result, expected):
            print(f"✓ Closure test => {get_result_value(result)}")
        else:
            print(f"✗ Closure test => Expected {expected}, got {result.inspect()}")
    print()


def test_classes():
    """Test class definitions and instantiation."""
    print("=== Test 3: Classes ===")
    
    tests = [
        # Simple class without constructor
        ("""
        clx SimpleClass {
            fx getValue(self) {
                return 42
            }
        }
        obj = SimpleClass()
        obj.getValue()
        """, 42),
        
        # Class with constructor
        ("""
        clx Person {
            fx __init__(self, name, age) {
                self.name = name
                self.age = age
            }
            
            fx getName(self) {
                return self.name
            }
            
            fx getAge(self) {
                return self.age
            }
        }
        
        p = Person("Alice", 30)
        p.getName()
        """, "Alice"),
        
        # Class instance field access
        ("""
        clx Counter {
            fx __init__(self, start) {
                self.count = start
            }
            
            fx increment(self) {
                self.count = self.count + 1
                return self.count
            }
        }
        
        c = Counter(10)
        c.increment()
        c.increment()
        """, 12),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ Class test => ERROR: {result.inspect()}")
        elif check_result(result, expected):
            print(f"✓ Class test => {get_result_value(result)}")
        else:
            print(f"✗ Class test => Expected {expected}, got {result.inspect()}")
    print()


def test_builtin_functions():
    """Test built-in functions comprehensively."""
    print("=== Test 4: Built-in Functions ===")
    
    # Test print function (it returns NIL)
    print("Testing print function:")
    result = eval_source('print("Hello, World!")')
    if result is NIL:
        print("✓ print() returns NIL")
    else:
        print(f"✗ print() should return NIL, got {result.inspect()}")
    
    # Test other built-ins
    tests = [
        ('len("hello world")', 11),
        ('len("")', 0),
        ('type(42)', "integer"),
        ('type("hello")', "string"),
        ('type(true)', "boolean"),
        ('type(nil)', "nil"),
        ('str(123)', "123"),
        ('str(true)', "true"),
        ('str(false)', "false"),
        ('int("42")', 42),
        ('int(true)', 1),
        ('int(false)', 0),
        ('bool(1)', True),
        ('bool(0)', False),
        ('bool("hello")', True),
        ('bool("")', False),
        ('bool(nil)', False),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ {source} => ERROR: {result.inspect()}")
        elif check_result(result, expected):
            print(f"✓ {source} => {get_result_value(result)}")
        else:
            print(f"✗ {source} => Expected {expected}, got {result.inspect()}")
    print()


def test_member_assignment():
    """Test member assignment (obj.field = value)."""
    print("=== Test 5: Member Assignment ===")
    
    tests = [
        ("""
        clx TestClass {
            fx __init__(self) {
                self.value = 0
            }
        }
        
        obj = TestClass()
        obj.value = 42
        obj.value
        """, 42),
        
        ("""
        clx Person {
            fx __init__(self, name) {
                self.name = name
            }
        }
        
        p = Person("Alice")
        p.name = "Bob"
        p.name
        """, "Bob"),
    ]
    
    for source, expected in tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✗ Member assignment test => ERROR: {result.inspect()}")
        elif check_result(result, expected):
            print(f"✓ Member assignment test => {get_result_value(result)}")
        else:
            print(f"✗ Member assignment test => Expected {expected}, got {result.inspect()}")
    print()


def test_error_cases():
    """Test various error cases."""
    print("=== Test 6: Error Cases ===")
    
    error_tests = [
        # Type errors
        "5 + true",
        '"Hello" - "World"',
        "-true",
        
        # Undefined variables
        "undefined_variable",
        
        # Wrong number of arguments
        'len("hello", "world")',
        'len()',
        
        # Calling non-functions
        "5()",
        '"hello"()',
        
        # Accessing non-existent members
        """
        clx TestClass { }
        obj = TestClass()
        obj.nonexistent_field
        """,
        
        # Self outside method
        "self",
        
        # Division by zero
        "10 / 0",
    ]
    
    for source in error_tests:
        result = eval_source(source)
        if isinstance(result, Error):
            print(f"✓ Error correctly caught: {source}")
        else:
            print(f"✗ Expected error for: {source}, got {result.inspect()}")
    print()


def eval_source(source: str):
    """Helper function to evaluate Zen source code."""
    try:
        # Remove extra whitespace and normalize
        source = " ".join(source.split())
        
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


def check_result(result, expected):
    """Check if result matches expected value."""
    if isinstance(result, Integer) and isinstance(expected, int):
        return result.value == expected
    elif isinstance(result, String) and isinstance(expected, str):
        return result.value == expected
    elif isinstance(result, Boolean) and isinstance(expected, bool):
        return result.value == expected
    else:
        return False


def get_result_value(result):
    """Get the Python value from a Zen object."""
    if isinstance(result, Integer):
        return result.value
    elif isinstance(result, String):
        return result.value
    elif isinstance(result, Boolean):
        return result.value
    else:
        return result.inspect()


if __name__ == "__main__":
    test_basic_functions()
    test_closures()
    test_classes()
    test_builtin_functions()
    test_member_assignment()
    test_error_cases()
    
    print("Advanced evaluator tests completed!") 