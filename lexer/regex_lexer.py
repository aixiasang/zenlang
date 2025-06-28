"""
Regex-based lexer for Zen language.
Inspired by Eli Bendersky's generic regex lexer.
"""

import re
from typing import List, Iterator, Optional, Tuple, Dict
from dataclasses import dataclass
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from zen_token import Token, TokenType, lookup_ident


class LexerError(Exception):
    """Lexer error exception."""
    
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at line {line}, column {column}: {message}")


class RegexLexer:
    """
    A regex-based lexer for Zen language.
    
    This implementation uses a single compiled regex with named groups
    to efficiently tokenize the input.
    """
    
    # Token rules: (regex_pattern, token_type, process_function)
    # Order matters! More specific patterns should come first
    TOKEN_RULES = [
        # Comments (skip these)
        (r'//[^\n]*', None, None),                    # Single-line comment
        (r'/\*[\s\S]*?\*/', None, None),              # Multi-line comment
        
        # Whitespace (track newlines for line counting)
        (r'\n', 'NEWLINE', None),                     # Newline
        (r'[ \t\r]+', None, None),                    # Other whitespace (skip)
        
        # String literals
        (r'"(?:[^"\\]|\\.)*"', TokenType.STRING, '_process_string'),
        
        # Numbers
        (r'\d+', TokenType.INT, '_process_int'),
        
        # Two-character operators (must come before single-char)
        (r'==', TokenType.EQ, None),
        (r'!=', TokenType.NEQ, None),
        (r'<=', TokenType.LTE, None),
        (r'>=', TokenType.GTE, None),
        (r'&&', TokenType.AND, None),
        (r'\|\|', TokenType.OR, None),
        
        # Single-character operators and delimiters
        (r'\+', TokenType.PLUS, None),
        (r'-', TokenType.MINUS, None),
        (r'\*', TokenType.MULTIPLY, None),
        (r'/', TokenType.DIVIDE, None),
        (r'=', TokenType.ASSIGN, None),
        (r'<', TokenType.LT, None),
        (r'>', TokenType.GT, None),
        (r'!', TokenType.NOT, None),
        (r'\(', TokenType.LPAREN, None),
        (r'\)', TokenType.RPAREN, None),
        (r'\{', TokenType.LBRACE, None),
        (r'\}', TokenType.RBRACE, None),
        (r',', TokenType.COMMA, None),
        (r'\.', TokenType.DOT, None),
        
        # Identifiers and keywords (must come last)
        (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENT_OR_KEYWORD', '_process_identifier'),
    ]
    
    def __init__(self):
        """Initialize the lexer and compile the master regex."""
        self._compile_regex()
        self.reset()
    
    def _compile_regex(self):
        """Compile all token rules into a single regex with named groups."""
        regex_parts = []
        self.group_type_map: Dict[str, str] = {}
        self.group_processor_map: Dict[str, Optional[str]] = {}
        
        for i, (pattern, token_type, processor) in enumerate(self.TOKEN_RULES):
            group_name = f'GROUP{i}'
            regex_parts.append(f'(?P<{group_name}>{pattern})')
            self.group_type_map[group_name] = token_type
            self.group_processor_map[group_name] = processor
        
        self.master_regex = re.compile('|'.join(regex_parts))
    
    def reset(self):
        """Reset lexer state."""
        self.input_text = ""
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self, input_text: str) -> List[Token]:
        """Tokenize input text and return list of tokens."""
        self.reset()
        self.input_text = input_text
        
        while self.position < len(self.input_text):
            self._next_token()
        
        # Add EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            literal=None,
            line=self.line,
            column=self.column
        ))
        
        return self.tokens
    
    def _next_token(self):
        """Process the next token from input."""
        # Try to match at current position
        match = self.master_regex.match(self.input_text, self.position)
        
        if not match:
            # No rule matched - illegal character
            char = self.input_text[self.position]
            raise LexerError(f"Illegal character: {repr(char)}", self.line, self.column)
        
        # Find which group matched
        matched_text = match.group(0)
        group_name = match.lastgroup
        token_type = self.group_type_map[group_name]
        processor = self.group_processor_map[group_name]
        
        # Handle special cases
        if token_type is None:
            # Skip this token (comment or whitespace)
            pass
        elif token_type == 'NEWLINE':
            # Track newlines for line counting
            self.line += 1
            self.column = 1
        else:
            # Process the token
            if processor:
                literal = getattr(self, processor)(matched_text)
            else:
                literal = matched_text
            
            # Create and add token
            token = Token(
                type=token_type,
                literal=literal,
                line=self.line,
                column=self.column
            )
            self.tokens.append(token)
        
        # Update position
        if token_type != 'NEWLINE':
            self.column += len(matched_text)
        self.position = match.end()
    
    def _process_string(self, text: str) -> str:
        """Process string literal by removing quotes and handling escapes."""
        # Remove surrounding quotes
        content = text[1:-1]
        
        # Process escape sequences
        escapes = {
            '\\n': '\n',
            '\\t': '\t',
            '\\r': '\r',
            '\\\\': '\\',
            '\\"': '"',
        }
        
        result = ""
        i = 0
        while i < len(content):
            if content[i] == '\\' and i + 1 < len(content):
                escape_seq = content[i:i+2]
                if escape_seq in escapes:
                    result += escapes[escape_seq]
                    i += 2
                else:
                    # Unknown escape, keep as is
                    result += content[i]
                    i += 1
            else:
                result += content[i]
                i += 1
        
        return result
    
    def _process_int(self, text: str) -> int:
        """Process integer literal."""
        return int(text)
    
    def _process_identifier(self, text: str) -> str:
        """Process identifier, checking if it's a keyword."""
        # This returns the identifier text, but we need to update token type
        # if it's a keyword. We'll handle this in _next_token.
        token_type = lookup_ident(text)
        
        # Update the last token's type if it's a keyword
        if hasattr(self, '_current_token_type'):
            self._current_token_type = token_type
        
        return text
    
    def _next_token_with_keyword_check(self):
        """Modified version that handles keyword checking."""
        match = self.master_regex.match(self.input_text, self.position)
        
        if not match:
            char = self.input_text[self.position]
            raise LexerError(f"Illegal character: {repr(char)}", self.line, self.column)
        
        matched_text = match.group(0)
        group_name = match.lastgroup
        token_type = self.group_type_map[group_name]
        processor = self.group_processor_map[group_name]
        
        if token_type is None:
            pass  # Skip
        elif token_type == 'NEWLINE':
            self.line += 1
            self.column = 1
        elif token_type == 'IDENT_OR_KEYWORD':
            # Special handling for identifiers/keywords
            actual_token_type = lookup_ident(matched_text)
            token = Token(
                type=actual_token_type,
                literal=matched_text,
                line=self.line,
                column=self.column
            )
            self.tokens.append(token)
        else:
            # Regular token processing
            if processor:
                literal = getattr(self, processor)(matched_text)
            else:
                literal = matched_text
            
            token = Token(
                type=token_type,
                literal=literal,
                line=self.line,
                column=self.column
            )
            self.tokens.append(token)
        
        if token_type != 'NEWLINE':
            self.column += len(matched_text)
        self.position = match.end()
    
    # Override _next_token with the keyword-aware version
    _next_token = _next_token_with_keyword_check


# Convenience function
def tokenize(input_text: str) -> List[Token]:
    """Convenience function to tokenize input text."""
    lexer = RegexLexer()
    return lexer.tokenize(input_text) 