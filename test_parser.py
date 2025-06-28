"""
Test script for Zen parser.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from zen_ast import *


def test_basic_parsing():
    """Test basic parsing."""
    print("Test 1: Basic function parsing")
    source = """
    fx add(a, b) {
        return a + b
    }
    """
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Source:\n{source}")
    print(f"Parsed AST:\n{program.string()}")
    print(f"Parser errors: {parser.errors}")
    print()


def test_package_and_load():
    """Test package and load statements."""
    print("Test 2: Package and load statements")
    source = """bag main
    
load("utils", "math")"""
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Source:\n{source}")
    print(f"Parsed AST:\n{program.string()}")
    print(f"Parser errors: {parser.errors}")
    print()


def test_class_parsing():
    """Test class parsing."""
    print("Test 3: Class parsing")
    source = """clx Person {
    fx __init__(self, name, age) {
        self.name = name
        self.age = age
    }
    
    fx GetName(self) {
        return self.name
    }
}"""
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Source:\n{source}")
    print(f"Parsed AST:\n{program.string()}")
    print(f"Parser errors: {parser.errors}")
    print()


def test_expressions():
    """Test expression parsing."""
    print("Test 4: Expression parsing")
    source = """
    a = 5
    b = a + 10
    c = a * b + 3
    result = add(a, b) + c.value
    """
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Source:\n{source}")
    print(f"Parsed AST:\n{program.string()}")
    print(f"Parser errors: {parser.errors}")
    print()


def test_operator_precedence():
    """Test operator precedence."""
    print("Test 5: Operator precedence")
    test_cases = [
        ("a + b * c", "(a + (b * c))"),
        ("a * b + c", "((a * b) + c)"),
        ("a + b * c + d", "((a + (b * c)) + d)"),
        ("a && b || c", "((a && b) || c)"),
        ("!-a", "(!(-a))"),
        ("a.b.c", "((a.b).c)"),
        ("add(a, b * c)", "add(a, (b * c))"),
    ]
    
    for source, expected in test_cases:
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        if program.statements:
            stmt = program.statements[0]
            if isinstance(stmt, ExpressionStatement):
                result = stmt.expression.string()
                status = "✓" if result == expected else "✗"
                print(f"  {status} '{source}' => {result} (expected: {expected})")
            else:
                print(f"  ✗ '{source}' => Not an expression statement")
        else:
            print(f"  ✗ '{source}' => No statements parsed")
    print()


def test_complex_program():
    """Test parsing a complex program."""
    print("Test 6: Complex program")
    source = """bag main

load("utils")

clx Calculator {
    fx __init__(self) {
        self.result = 0
    }
    
    fx Add(self, a, b) {
        self.result = a + b
        return self.result
    }
    
    fx Multiply(self, a, b) {
        self.result = a * b
        return self.result
    }
}

fx main() {
    calc = Calculator()
    sum = calc.Add(5, 3)
    product = calc.Multiply(sum, 2)
    print("Result: " + product)
}"""
    
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Source:\n{source}")
    print(f"\nParsed AST:\n{program.string()}")
    print(f"\nNumber of statements: {len(program.statements)}")
    print(f"Parser errors: {parser.errors}")
    
    # Analyze the parsed structure
    for i, stmt in enumerate(program.statements):
        print(f"\nStatement {i}: {type(stmt).__name__}")
        if isinstance(stmt, PackageStatement):
            print(f"  Package name: {stmt.name}")
        elif isinstance(stmt, LoadStatement):
            print(f"  Imports: {stmt.imports}")
        elif isinstance(stmt, ClassStatement):
            print(f"  Class name: {stmt.name}")
            print(f"  Methods: {[m.name for m in stmt.methods]}")
        elif isinstance(stmt, FunctionStatement):
            print(f"  Function name: {stmt.name}")
            print(f"  Parameters: {stmt.parameters}")


if __name__ == "__main__":
    test_basic_parsing()
    test_package_and_load()
    test_class_parsing()
    test_expressions()
    test_operator_precedence()
    test_complex_program()
    
    print("\nAll parser tests completed!") 