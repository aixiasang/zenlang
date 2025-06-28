#!/usr/bin/env python3
"""
Zen Module System Demo
Demonstrates the complete module system functionality.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator, eval_node
from evaluator.evaluator import apply_function
from object import Environment, Error


def run_zen_file_with_modules(file_path: str):
    """
    Run a Zen file that may use the module system.
    
    Args:
        file_path: Path to the Zen file to execute
    """
    print(f"Running Zen file: {file_path}")
    print("=" * 60)
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Parse the source
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        # Check for parse errors
        if parser.errors:
            print("Parse Errors:")
            for error in parser.errors:
                print(f"  - {error}")
            return False
        
        # Create evaluator and environment
        evaluator = Evaluator()
        env = Environment()
        
        # Copy built-in functions to environment
        for name, builtin in evaluator.globals.items():
            env.set(name, builtin)
        
        # Evaluate the program
        result = eval_node(program, env)
        
        # Check for runtime errors
        if isinstance(result, Error):
            print(f"Runtime Error: {result.message}")
            return False
        
        # Look for and execute main function if it exists
        main_function = env.get("main")
        if main_function:
            print("\nExecuting main function...")
            print("-" * 40)
            main_result = apply_function(main_function, [], env)
            
            if isinstance(main_result, Error):
                print(f"Main function error: {main_result.message}")
                return False
            else:
                print(f"\nMain function returned: {main_result.inspect()}")
        
        print("\nProgram completed successfully!")
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


def demonstrate_module_system():
    """Demonstrate the complete module system."""
    print("=" * 60)
    print("ZEN LANGUAGE MODULE SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Test the module test file
    module_test_file = "examples/module_test.zen"
    
    if os.path.exists(module_test_file):
        print("\n1. Running comprehensive module test...")
        success = run_zen_file_with_modules(module_test_file)
        if not success:
            print("Module test failed!")
            return False
    else:
        print(f"Module test file '{module_test_file}' not found.")
        return False
    
    print("\n" + "=" * 60)
    print("2. Testing individual components...")
    
    # Test basic math module
    if os.path.exists("examples/math_simple.zen"):
        print("\n✓ Math simple module found")
        # Try to load and inspect math module
        try:
            from evaluator.evaluator import load_module
            env = Environment()
            evaluator = Evaluator()
            
            # Copy builtins
            for name, builtin in evaluator.globals.items():
                env.set(name, builtin)
            
            module = load_module("math_simple", env)
            if isinstance(module, Error):
                print(f"Error loading math_simple module: {module.message}")
            else:
                print(f"✓ Math simple module loaded successfully: {module.inspect()}")
                
                # List public members
                public_members = module.get_public_members()
                print(f"  Public members: {list(public_members.keys())}")
                
        except Exception as e:
            print(f"Error testing math_simple module: {e}")
    
    # Test utils module
    if os.path.exists("examples/utils.zen"):
        print("\n✓ Utils module found")
    
    print("\n" + "=" * 60)
    print("Module system demonstration complete!")
    print("=" * 60)
    
    return True


def interactive_module_demo():
    """Interactive demonstration of module features."""
    print("\n" + "=" * 60)
    print("INTERACTIVE MODULE DEMO")
    print("=" * 60)
    
    # Simple interactive code that uses modules
    demo_code = '''
bag main

load("math_simple")

fx main() {
    print("=== Interactive Module Demo ===")
    
         // Use math module
     result = math_simple.Add(10, 20)
     print("math_simple.Add(10, 20) =", result)
     
     // Test Transform function
     transform_result = math_simple.Transform(5)
     print("math_simple.Transform(5) =", transform_result)
    
    print("Demo complete!")
    return result
}
'''
    
    print("Running interactive demo code:")
    print("-" * 40)
    
    try:
        lexer = Lexer(demo_code)
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
        
        # Evaluate
        result = eval_node(program, env)
        
        if isinstance(result, Error):
            print(f"Error: {result.message}")
            return False
        
        # Execute main
        main_fn = env.get("main")
        if main_fn:
            main_result = apply_function(main_fn, [], env)
            if isinstance(main_result, Error):
                print(f"Main error: {main_result.message}")
                return False
            
            print(f"\nDemo returned: {main_result.inspect()}")
        
        return True
        
    except Exception as e:
        print(f"Demo error: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run specific file
        file_path = sys.argv[1]
        success = run_zen_file_with_modules(file_path)
        sys.exit(0 if success else 1)
    else:
        # Run full demonstration
        print("Starting Zen Module System Demo...")
        
        success = demonstrate_module_system()
        
        if success:
            interactive_module_demo()
        
        print("\nDemo finished!")
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 