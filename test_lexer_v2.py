"""
Test script for the new version of Zen lexer.
"""

from lexer.lexer_v2 import Lexer, TokenType


def test_basic():
    """Test basic tokenization."""
    print("Test 1: Basic tokens")
    source = "fx add(a,b){ return a+b }"
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    
    print(f"Source: {source}")
    print("Tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token}")
    
    # Verify expected tokens
    expected_types = [
        TokenType.FX,
        TokenType.IDENT,  # add
        TokenType.LPAREN,
        TokenType.IDENT,  # a
        TokenType.COMMA,
        TokenType.IDENT,  # b
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RETURN,
        TokenType.IDENT,  # a
        TokenType.PLUS,
        TokenType.IDENT,  # b
        TokenType.RBRACE,
        TokenType.EOF
    ]
    
    print("\nExpected vs Actual:")
    for i, (token, expected) in enumerate(zip(tokens, expected_types)):
        status = "✓" if token.type == expected else "✗"
        print(f"  {status} Position {i}: Expected {expected}, Got {token.type}")
    print()


def test_comments():
    """Test comment handling."""
    print("Test 2: Comments")
    source = """// This is a comment
fx test() {
    /* Multi-line
       comment */
    return 42
}"""
    lexer = Lexer(source)
    tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
    
    print(f"Source:\n{source}")
    print("\nTokens (comments should be skipped):")
    for token in tokens:
        print(f"  {token}")
    print()


def test_string_literals():
    """Test string literals."""
    print("Test 3: String literals")
    source = '"Hello, World!" "Escaped\\"Quote" "Newline\\nTest"'
    lexer = Lexer(source)
    tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
    
    print(f"Source: {source}")
    print("Tokens:")
    for token in tokens:
        print(f"  {token} - actual value: {repr(token.literal)}")
    print()


def test_operators():
    """Test operator recognition."""
    print("Test 4: Operators")
    source = "+ - * / = == != < > <= >= && || !"
    lexer = Lexer(source)
    tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
    
    print(f"Source: {source}")
    print("Tokens:")
    for token in tokens:
        print(f"  {token}")
    print()


def test_keywords():
    """Test keyword recognition."""
    print("Test 5: Keywords")
    source = "bag load fx clx return if else for true false nil self"
    lexer = Lexer(source)
    tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
    
    print(f"Source: {source}")
    print("Tokens:")
    for token in tokens:
        print(f"  {token}")
    print()


def test_complex_program():
    """Test a complex Zen program."""
    print("Test 6: Complex Zen program")
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
    print(p.GetName())
}"""
    
    lexer = Lexer(source)
    tokens = lexer.get_tokens()
    
    print(f"Source:\n{source}")
    print(f"\nTotal tokens: {len(tokens)}")
    print("\nFirst 30 tokens:")
    for i, token in enumerate(tokens[:30]):
        print(f"  {i}: {token}")
    print()


if __name__ == "__main__":
    test_basic()
    test_comments()
    test_string_literals()
    test_operators()
    test_keywords()
    test_complex_program()
    
    print("All tests completed!") 