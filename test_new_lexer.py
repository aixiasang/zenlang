"""
Test script for the new regex-based Zen lexer.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, LexerError
from zen_token import TokenType


def test_basic_tokens():
    """Test basic token recognition."""
    print("=== Test 1: Basic tokens ===")
    source = "fx add(a,b){ return a+b }"
    
    try:
        lexer = Lexer(source)
        tokens = lexer.get_tokens()
        
        print(f"Source: {source}")
        print("Tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i}: {token}")
        
        # Verify expected sequence
        expected_types = [
            TokenType.FX, TokenType.IDENT, TokenType.LPAREN, TokenType.IDENT,
            TokenType.COMMA, TokenType.IDENT, TokenType.RPAREN, TokenType.LBRACE,
            TokenType.RETURN, TokenType.IDENT, TokenType.PLUS, TokenType.IDENT,
            TokenType.RBRACE, TokenType.EOF
        ]
        
        print("\nValidation:")
        for i, (token, expected) in enumerate(zip(tokens, expected_types)):
            status = "✓" if token.type == expected else "✗"
            print(f"  {status} {i}: Expected {expected}, Got {token.type}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


def test_comments():
    """Test comment handling."""
    print("=== Test 2: Comments ===")
    source = """// Single line comment
fx test() {
    /* Multi-line
       comment */
    return 42
}"""
    
    try:
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        print(f"Source:\n{source}")
        print("\nTokens (comments should be skipped):")
        for token in tokens:
            print(f"  {token}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


def test_string_literals():
    """Test string literal parsing."""
    print("=== Test 3: String literals ===")
    source = '"Hello, World!" "Escaped\\"Quote" "Newline\\nTest"'
    
    try:
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        print(f"Source: {source}")
        print("Tokens:")
        for token in tokens:
            print(f"  {token} => actual value: {repr(token.literal)}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


def test_operators():
    """Test operator recognition."""
    print("=== Test 4: Operators ===")
    source = "+ - * / = == != < > <= >= && || !"
    
    try:
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        print(f"Source: {source}")
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


def test_keywords():
    """Test keyword recognition."""
    print("=== Test 5: Keywords ===")
    source = "bag load fx clx return if else for true false nil self"
    
    try:
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        print(f"Source: {source}")
        print("Tokens:")
        for token in tokens:
            print(f"  {token}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


def test_error_handling():
    """Test error handling."""
    print("=== Test 6: Error handling ===")
    source = 'valid_code = "string" @ invalid_char #'
    
    try:
        lexer = Lexer(source)
        tokens = lexer.get_tokens()
        
        print(f"Source: {source}")
        print("This should have caused an error!")
        
    except LexerError as e:
        print(f"Source: {source}")
        print(f"Expected lexer error: {e}")
    print()


def test_complex_program():
    """Test a complex Zen program."""
    print("=== Test 7: Complex program ===")
    source = """bag main

load("utils")

clx Person {
    fx __init__(self, name, age) {
        self.name = name
        self.age = age
    }
    
    fx GetName(self) {
        return self.name
    }
}

fx main() {
    p = Person("Alice", 30)
    result = p.GetName()
    print("Name: " + result)
}"""
    
    try:
        lexer = Lexer(source)
        tokens = lexer.get_tokens()
        
        print(f"Source:\n{source}")
        print(f"\nTotal tokens: {len(tokens)}")
        print("\nFirst 20 tokens:")
        for i, token in enumerate(tokens[:20]):
            print(f"  {i}: {token}")
        
        print(f"\nLast 5 tokens:")
        for i, token in enumerate(tokens[-5:], len(tokens)-5):
            print(f"  {i}: {token}")
        
    except LexerError as e:
        print(f"Lexer error: {e}")
    print()


if __name__ == "__main__":
    test_basic_tokens()
    test_comments()
    test_string_literals()
    test_operators()
    test_keywords()
    test_error_handling()
    test_complex_program()
    
    print("All lexer tests completed!") 