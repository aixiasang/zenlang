#!/usr/bin/env python3
"""
Zen Language Feature Demonstration
This script demonstrates all the currently implemented features of the Zen interpreter.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import Evaluator, eval_node
from object import Environment, Error


def demo_section(title, source_code):
    """Run a demo section."""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")
    print(f"Code:\n{source_code}")
    print(f"\nOutput:")
    
    try:
        evaluator = Evaluator()
        environment = Environment()
        
        # Setup builtins
        for name, builtin in evaluator.globals.items():
            environment.set(name, builtin)
        
        # Parse and evaluate
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if parser.errors:
            print("Parse Errors:")
            for error in parser.errors:
                print(f"  {error}")
            return
        
        result = eval_node(program, environment)
        
        if isinstance(result, Error):
            print(f"Runtime Error: {result.message}")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all demos."""
    print("Zen Language Interpreter - Feature Demonstration")
    print("=" * 60)
    
    # Demo 1: Basic arithmetic and variables
    demo_section("1. Basic Arithmetic and Variables", """
// Variables and arithmetic
a = 10
b = 20
sum = a + b
difference = b - a
product = a * b
quotient = b / a

print("a =", a)
print("b =", b)
print("a + b =", sum)
print("b - a =", difference)
print("a * b =", product)
print("b / a =", quotient)
""")
    
    # Demo 2: String operations
    demo_section("2. String Operations", """
// String operations
first_name = "Alice"
last_name = "Johnson"
full_name = first_name + " " + last_name

print("First name:", first_name)
print("Last name:", last_name)
print("Full name:", full_name)
print("Length of full name:", len(full_name))

// String comparison
print("Names equal?", first_name == last_name)
print("Names different?", first_name != last_name)
""")
    
    # Demo 3: Boolean logic
    demo_section("3. Boolean Logic and Comparisons", """
// Boolean operations
x = 15
y = 10

print("x =", x, ", y =", y)
print("x > y:", x > y)
print("x < y:", x < y)
print("x == y:", x == y)
print("x != y:", x != y)

// Logical operators
condition1 = x > 5
condition2 = y < 20
print("x > 5:", condition1)
print("y < 20:", condition2)
print("Both true:", condition1 && condition2)
print("Either true:", condition1 || condition2)
print("Not condition1:", !condition1)
""")
    
    # Demo 4: Functions
    demo_section("4. Functions and Closures", """
// Basic function
fx add(a, b) {
    return a + b
}

fx multiply(a, b) {
    return a * b
}

// Function calls
result1 = add(5, 3)
result2 = multiply(4, 6)

print("add(5, 3) =", result1)
print("multiply(4, 6) =", result2)

// Nested function call
result3 = add(result1, result2)
print("add(8, 24) =", result3)

// Function without explicit return
fx get_constant() {
    42
}

constant = get_constant()
print("Constant value:", constant)
""")
    
    # Demo 5: Classes and objects (basic version)
    demo_section("5. Classes and Objects", """
// Simple class
clx Calculator {
    fx add(self, a, b) {
        return a + b
    }
    
    fx multiply(self, a, b) {
        return a * b
    }
}

calc = Calculator()
sum_result = calc.add(10, 5)
mult_result = calc.multiply(3, 7)

print("Calculator.add(10, 5) =", sum_result)
print("Calculator.multiply(3, 7) =", mult_result)
""")
    
    # Demo 6: Built-in functions
    demo_section("6. Built-in Functions", """
// Type checking
print("Type of 42:", type(42))
print("Type of 'hello':", type("hello"))
print("Type of true:", type(true))
print("Type of nil:", type(nil))

// Type conversions
print("String of 123:", str(123))
print("String of true:", str(true))
print("Integer of '456':", int("456"))
print("Boolean of 1:", bool(1))
print("Boolean of 0:", bool(0))
print("Boolean of 'text':", bool("text"))
print("Boolean of '':", bool(""))

// String functions
text = "Hello, Zen!"
print("Text:", text)
print("Length:", len(text))
""")
    
    # Demo 7: Error handling
    demo_section("7. Error Handling Examples", """
// These would produce errors (commented out):
// print("Type error:", 5 + "hello")
// print("Unknown variable:", undefined_var)
// print("Division by zero:", 10 / 0)

// Valid operations
print("Valid: 5 + 5 =", 5 + 5)
print("Valid: 'hello' + ' world' =", "hello" + " world")
""")
    
    print(f"\n{'='*60}")
    print(" Demo Complete!")
    print(f"{'='*60}")
    print("\nTo try the interactive REPL, run: python zen_repl.py")
    print("To run a Zen file, run: python zen_repl.py filename.zen")


if __name__ == "__main__":
    main() 