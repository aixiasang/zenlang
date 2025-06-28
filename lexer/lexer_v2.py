"""
Lexer module for Zen language - Version 2.
A simpler implementation using individual pattern matching.
"""

import re
from typing import List, Optional, Tuple
from dataclasses import dataclass


class TokenType:
    """All token types in Zen language."""
    
    # Special tokens
    EOF = 'EOF'
    ILLEGAL = 'ILLEGAL'
    
    # Identifiers and literals
    IDENT = 'IDENT'
    INT = 'INT'
    STRING = 'STRING'
    
    # Keywords
    BAG = 'BAG'
    LOAD = 'LOAD'
    FX = 'FX'
    CLX = 'CLX'
    RETURN = 'RETURN'
    IF = 'IF'
    ELSE = 'ELSE'
    FOR = 'FOR'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NIL = 'NIL'
    SELF = 'SELF'
    
    # Operators
    ASSIGN = 'ASSIGN'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    MULTIPLY = 'MULTIPLY'
    DIVIDE = 'DIVIDE'
    
    # Comparison operators
    EQ = 'EQ'
    NEQ = 'NEQ'
    LT = 'LT'
    GT = 'GT'
    LTE = 'LTE'
    GTE = 'GTE'
    
    # Logical operators
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    # Delimiters
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACE = 'LBRACE'
    RBRACE = 'RBRACE'
    COMMA = 'COMMA'
    DOT = 'DOT'


# Keywords mapping
KEYWORDS = {
    'bag': TokenType.BAG,
    'load': TokenType.LOAD,
    'fx': TokenType.FX,
    'clx': TokenType.CLX,
    'return': TokenType.RETURN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'nil': TokenType.NIL,
    'self': TokenType.SELF,
}


@dataclass
class Token:
    """Represents a token in the source code."""
    type: str
    literal: any
    line: int = 1
    column: int = 1
    
    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.literal)})"


class Lexer:
    """Lexical analyzer for Zen language."""
    
    def __init__(self, source: str):
        """Initialize lexer with source code."""
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self._tokenize()
    
    def _current_char(self) -> Optional[str]:
        """Get current character."""
        if self.position >= len(self.source):
            return None
        return self.source[self.position]
    
    def _peek_char(self, offset=1) -> Optional[str]:
        """Peek at character ahead."""
        pos = self.position + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def _advance(self):
        """Advance position and update line/column."""
        if self.position < len(self.source):
            if self.source[self.position] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1
    
    def _skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self._current_char() in ' \t\r':
            self._advance()
    
    def _skip_single_line_comment(self):
        """Skip single-line comment."""
        # Skip //
        self._advance()
        self._advance()
        
        # Skip until newline
        while self._current_char() and self._current_char() != '\n':
            self._advance()
    
    def _skip_multi_line_comment(self):
        """Skip multi-line comment."""
        # Skip /*
        self._advance()
        self._advance()
        
        # Skip until */
        while self._current_char():
            if self._current_char() == '*' and self._peek_char() == '/':
                self._advance()  # Skip *
                self._advance()  # Skip /
                break
            self._advance()
    
    def _read_string(self) -> str:
        """Read string literal."""
        # Skip opening quote
        self._advance()
        
        value = ""
        while self._current_char() and self._current_char() != '"':
            if self._current_char() == '\\':
                self._advance()
                # Handle escape sequences
                if self._current_char() == 'n':
                    value += '\n'
                elif self._current_char() == 't':
                    value += '\t'
                elif self._current_char() == 'r':
                    value += '\r'
                elif self._current_char() == '\\':
                    value += '\\'
                elif self._current_char() == '"':
                    value += '"'
                else:
                    # Unknown escape, keep as is
                    value += self._current_char()
                self._advance()
            else:
                value += self._current_char()
                self._advance()
        
        # Skip closing quote
        if self._current_char() == '"':
            self._advance()
        
        return value
    
    def _read_number(self) -> int:
        """Read integer literal."""
        start_pos = self.position
        
        while self._current_char() and self._current_char().isdigit():
            self._advance()
        
        return int(self.source[start_pos:self.position])
    
    def _read_identifier(self) -> str:
        """Read identifier or keyword."""
        start_pos = self.position
        
        # First character must be letter or underscore
        if self._current_char().isalpha() or self._current_char() == '_':
            self._advance()
            
            # Rest can be letters, digits, or underscores
            while self._current_char() and (self._current_char().isalnum() or self._current_char() == '_'):
                self._advance()
        
        return self.source[start_pos:self.position]
    
    def _add_token(self, token_type: str, literal: any):
        """Add a token to the list."""
        self.tokens.append(Token(
            type=token_type,
            literal=literal,
            line=self.line,
            column=self.column - len(str(literal)) if isinstance(literal, str) else self.column - 1
        ))
    
    def _tokenize(self):
        """Tokenize the entire source code."""
        while self.position < len(self.source):
            self._skip_whitespace()
            
            char = self._current_char()
            if not char:
                break
            
            # Skip newlines
            if char == '\n':
                self._advance()
                continue
            
            # Comments
            if char == '/' and self._peek_char() == '/':
                self._skip_single_line_comment()
                continue
            
            if char == '/' and self._peek_char() == '*':
                self._skip_multi_line_comment()
                continue
            
            # String literals
            if char == '"':
                string_value = self._read_string()
                self._add_token(TokenType.STRING, string_value)
                continue
            
            # Number literals
            if char.isdigit():
                number_value = self._read_number()
                self._add_token(TokenType.INT, number_value)
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                ident = self._read_identifier()
                token_type = KEYWORDS.get(ident, TokenType.IDENT)
                self._add_token(token_type, ident)
                continue
            
            # Two-character operators
            if char == '=' and self._peek_char() == '=':
                self._add_token(TokenType.EQ, '==')
                self._advance()
                self._advance()
                continue
            
            if char == '!' and self._peek_char() == '=':
                self._add_token(TokenType.NEQ, '!=')
                self._advance()
                self._advance()
                continue
            
            if char == '<' and self._peek_char() == '=':
                self._add_token(TokenType.LTE, '<=')
                self._advance()
                self._advance()
                continue
            
            if char == '>' and self._peek_char() == '=':
                self._add_token(TokenType.GTE, '>=')
                self._advance()
                self._advance()
                continue
            
            if char == '&' and self._peek_char() == '&':
                self._add_token(TokenType.AND, '&&')
                self._advance()
                self._advance()
                continue
            
            if char == '|' and self._peek_char() == '|':
                self._add_token(TokenType.OR, '||')
                self._advance()
                self._advance()
                continue
            
            # Single-character tokens
            single_char_tokens = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '!': TokenType.NOT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
            }
            
            if char in single_char_tokens:
                self._add_token(single_char_tokens[char], char)
                self._advance()
                continue
            
            # Illegal character
            self._add_token(TokenType.ILLEGAL, char)
            self._advance()
        
        # Add EOF token
        self._add_token(TokenType.EOF, None)
    
    def get_tokens(self) -> List[Token]:
        """Get all tokens."""
        return self.tokens 