"""
Lexer module for Zen language.
Uses an improved regex-based implementation for better performance and clarity.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
from .regex_lexer import RegexLexer, LexerError, tokenize
from zen_token import Token, TokenType


class Lexer:
    """
    Main Lexer class for Zen language.
    
    This is a wrapper around RegexLexer to maintain backward compatibility
    while providing an improved implementation.
    """
    
    def __init__(self, source: str):
        """Initialize lexer with source code."""
        self.source = source
        self.regex_lexer = RegexLexer()
        self.tokens = self.regex_lexer.tokenize(source)
        self.position = 0
    
    def get_tokens(self) -> List[Token]:
        """Get all tokens."""
        return self.tokens
    
    def next_token(self) -> Token:
        """Get next token (for compatibility with streaming interface)."""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        else:
            # Return EOF token
            return Token(type=TokenType.EOF, literal=None)
    
    def peek_token(self, offset: int = 0) -> Token:
        """Peek at token at current position + offset."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        else:
            return Token(type=TokenType.EOF, literal=None)
    
    def __iter__(self):
        """Make lexer iterable."""
        return iter(self.tokens)
    
    def reset(self):
        """Reset position to beginning."""
        self.position = 0


# Export classes and functions for backward compatibility
__all__ = ['Lexer', 'LexerError', 'Token', 'TokenType', 'tokenize'] 