#!/usr/bin/env python3
"""
Test suite for Zen language module system.
Tests package declarations, module loading, and visibility rules.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator, eval_node
from object import Environment, ObjectType, Error, String, Integer, Module


def test_basic_module_loading():
    """Test basic module loading functionality."""
    print("Testing basic module loading...")
    
    # Create a simple module
    math_module_code = '''
bag math

fx Add(a, b) {
    return a + b
}

PI = 314159
'''
    
    # Write to file
    with open('examples/test_math.zen', 'w', encoding='utf-8') as f:
        f.write(math_module_code)
    
    # Create main code that loads the module
    main_code = '''
bag main

load("test_math")

fx main() {
    result = test_math.Add(5, 3)
    print("Result:", result)
    print("PI:", test_math.PI)
    return result
}
'''
    
    try:
        # Parse and evaluate
        lexer = Lexer(main_code)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            print(f"Parse errors: {parser.errors}")
            return False
        
        evaluator = Evaluator()
        env = Environment()
        
        # Copy builtins
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        # Evaluate the program
        result = eval_node(program, env)
        
        if isinstance(result, Error):
            print(f"Evaluation error: {result.message}")
            return False
        
        # Check if module was loaded
        module_obj = env.get("test_math")
        if not isinstance(module_obj, Module):
            print("Module was not loaded properly")
            return False
        
        # Call main function
        main_fn = env.get("main")
        if main_fn:
            from evaluator.evaluator import apply_function
            main_result = apply_function(main_fn, [], env)
            if isinstance(main_result, Error):
                print(f"Main function error: {main_result.message}")
                return False
        
        print("✓ Basic module loading test passed")
        return True
        
    except Exception as e:
        print(f"Exception during test: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists('examples/test_math.zen'):
            os.remove('examples/test_math.zen')


def test_visibility_rules():
    """Test public/private visibility rules."""
    print("Testing visibility rules...")
    
    # Create module with public and private members
    visibility_module_code = '''
bag visibility_test

// Public function (uppercase)
fx PublicFunction() {
    return "public"
}

// Private function (lowercase)
fx privateFunction() {
    return "private"
}

// Public constant
PUBLIC_CONSTANT = 42

// Private constant
private_constant = 24
'''
    
    with open('examples/visibility_test.zen', 'w', encoding='utf-8') as f:
        f.write(visibility_module_code)
    
    # Main code that tests visibility
    main_code = '''
load("visibility_test")

fx main() {
    // This should work
    result1 = visibility_test.PublicFunction()
    print("Public function:", result1)
    
    constant1 = visibility_test.PUBLIC_CONSTANT
    print("Public constant:", constant1)
    
    return result1
}
'''
    
    try:
        lexer = Lexer(main_code)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            print(f"Parse errors: {parser.errors}")
            return False
        
        evaluator = Evaluator()
        env = Environment()
        
        # Copy builtins
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        result = eval_node(program, env)
        
        if isinstance(result, Error):
            print(f"Evaluation error: {result.message}")
            return False
        
        # Check module was loaded
        module_obj = env.get("visibility_test")
        if not isinstance(module_obj, Module):
            print("Module was not loaded")
            return False
        
        # Check public members are accessible
        public_fn = module_obj.get_member("PublicFunction")
        if public_fn is None:
            print("Public function not accessible")
            return False
        
        public_const = module_obj.get_member("PUBLIC_CONSTANT")
        if public_const is None:
            print("Public constant not accessible")
            return False
        
        # Check private members are NOT accessible
        private_fn = module_obj.get_member("privateFunction")
        if private_fn is not None:
            print("Private function should not be accessible")
            return False
        
        private_const = module_obj.get_member("private_constant")
        if private_const is not None:
            print("Private constant should not be accessible")
            return False
        
        print("✓ Visibility rules test passed")
        return True
        
    except Exception as e:
        print(f"Exception during test: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists('examples/visibility_test.zen'):
            os.remove('examples/visibility_test.zen')


def test_module_caching():
    """Test that modules are cached and not reloaded."""
    print("Testing module caching...")
    
    # Create a module with a counter
    counter_module_code = '''
bag counter

counter_value = 0

fx Increment() {
    counter_value = counter_value + 1
    return counter_value
}

fx GetValue() {
    return counter_value
}
'''
    
    with open('examples/counter.zen', 'w', encoding='utf-8') as f:
        f.write(counter_module_code)
    
    # Main code that loads the same module twice
    main_code = '''
load("counter")
load("counter")  // Should use cached version

fx main() {
    // Increment counter
    counter.Increment()
    counter.Increment()
    value = counter.GetValue()
    print("Counter value:", value)
    return value
}
'''
    
    try:
        lexer = Lexer(main_code)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            print(f"Parse errors: {parser.errors}")
            return False
        
        evaluator = Evaluator()
        env = Environment()
        
        # Copy builtins
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        result = eval_node(program, env)
        
        if isinstance(result, Error):
            print(f"Evaluation error: {result.message}")
            return False
        
        print("✓ Module caching test passed")
        return True
        
    except Exception as e:
        print(f"Exception during test: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists('examples/counter.zen'):
            os.remove('examples/counter.zen')


def test_circular_import_detection():
    """Test detection of circular imports."""
    print("Testing circular import detection...")
    
    # Create two modules that import each other
    module_a_code = '''
bag module_a

load("module_b")

fx FunctionA() {
    return "A"
}
'''
    
    module_b_code = '''
bag module_b

load("module_a")

fx FunctionB() {
    return "B"
}
'''
    
    with open('examples/module_a.zen', 'w', encoding='utf-8') as f:
        f.write(module_a_code)
    
    with open('examples/module_b.zen', 'w', encoding='utf-8') as f:
        f.write(module_b_code)
    
    # Main code that tries to load module with circular dependency
    main_code = '''
load("module_a")

fx main() {
    return "Should not reach here"
}
'''
    
    try:
        lexer = Lexer(main_code)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            print(f"Parse errors: {parser.errors}")
            return False
        
        evaluator = Evaluator()
        env = Environment()
        
        # Copy builtins
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        result = eval_node(program, env)
        
        # Should get an error about circular import
        if isinstance(result, Error) and "Circular import" in result.message:
            print("✓ Circular import detection test passed")
            return True
        else:
            print("Should have detected circular import")
            return False
        
    except Exception as e:
        print(f"Exception during test: {e}")
        return False
    finally:
        # Cleanup
        for filename in ['examples/module_a.zen', 'examples/module_b.zen']:
            if os.path.exists(filename):
                os.remove(filename)


def run_all_module_tests():
    """Run all module system tests."""
    print("=" * 50)
    print("Running Zen Module System Tests")
    print("=" * 50)
    
    tests = [
        test_basic_module_loading,
        test_visibility_rules,
        test_module_caching,
        test_circular_import_detection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Module Tests: {passed}/{total} passed")
    print("=" * 50)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_module_tests()
    sys.exit(0 if success else 1) 