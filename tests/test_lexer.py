"""
Tests for the Zen language lexer.
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from zen_token import TokenType


class TestLexer(unittest.TestCase):
    """Test cases for the lexer."""
    
    def test_basic_tokens(self):
        """Test basic token recognition."""
        source = "fx add(a,b){ return a+b }"
        lexer = Lexer(source)
        tokens = lexer.get_tokens()
        
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
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, (token, expected_type) in enumerate(zip(tokens, expected_types)):
            self.assertEqual(token.type, expected_type, 
                           f"Token {i}: expected {expected_type}, got {token.type}")
    
    def test_comments(self):
        """Test single-line and multi-line comments."""
        source = """
        // This is a single-line comment
        fx test() {
            /* This is a
               multi-line comment */
            return 42
        }
        """
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        # Comments should be skipped
        self.assertEqual(tokens[0].type, TokenType.FX)
        self.assertEqual(tokens[1].type, TokenType.IDENT)
        self.assertEqual(tokens[1].literal, "test")
    
    def test_string_literals(self):
        """Test string literal parsing."""
        source = '"Hello, World!" "Escaped\\"Quote" "Newline\\nTest"'
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[0].type, TokenType.STRING)
        self.assertEqual(tokens[0].literal, "Hello, World!")
        self.assertEqual(tokens[1].type, TokenType.STRING)
        self.assertEqual(tokens[1].literal, 'Escaped"Quote')
        self.assertEqual(tokens[2].type, TokenType.STRING)
        self.assertEqual(tokens[2].literal, "Newline\nTest")
    
    def test_integer_literals(self):
        """Test integer literal parsing."""
        source = "123 456 0 42"
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0].literal, 123)
        self.assertEqual(tokens[1].literal, 456)
        self.assertEqual(tokens[2].literal, 0)
        self.assertEqual(tokens[3].literal, 42)
    
    def test_keywords(self):
        """Test keyword recognition."""
        source = "bag load fx clx return if else for true false nil self"
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        expected_types = [
            TokenType.BAG, TokenType.LOAD, TokenType.FX, TokenType.CLX,
            TokenType.RETURN, TokenType.IF, TokenType.ELSE, TokenType.FOR,
            TokenType.TRUE, TokenType.FALSE, TokenType.NIL, TokenType.SELF
        ]
        
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)
    
    def test_operators(self):
        """Test operator recognition."""
        source = "+ - * / = == != < > <= >= && || !"
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
            TokenType.ASSIGN, TokenType.EQ, TokenType.NEQ,
            TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE,
            TokenType.AND, TokenType.OR, TokenType.NOT
        ]
        
        for token, expected_type in zip(tokens, expected_types):
            self.assertEqual(token.type, expected_type)
    
    def test_complex_expression(self):
        """Test a complex expression."""
        source = """
        bag main
        
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
        }
        """
        lexer = Lexer(source)
        tokens = lexer.get_tokens()
        
        # Just verify it doesn't crash and produces reasonable tokens
        self.assertTrue(len(tokens) > 50)
        self.assertEqual(tokens[0].type, TokenType.BAG)
        self.assertEqual(tokens[1].type, TokenType.IDENT)
        self.assertEqual(tokens[1].literal, "main")
        self.assertEqual(tokens[-1].type, TokenType.EOF)
    
    def test_line_and_column_tracking(self):
        """Test that line and column numbers are tracked correctly."""
        source = "fx\nadd(a,\nb)"
        lexer = Lexer(source)
        tokens = [t for t in lexer.get_tokens() if t.type != TokenType.EOF]
        
        # fx on line 1
        self.assertEqual(tokens[0].line, 1)
        self.assertEqual(tokens[0].column, 1)
        
        # add on line 2
        self.assertEqual(tokens[1].line, 2)
        self.assertEqual(tokens[1].column, 1)
        
        # b on line 3
        self.assertEqual(tokens[5].line, 3)
        self.assertEqual(tokens[5].column, 1)


if __name__ == '__main__':
    unittest.main() 