"""
Token module for Zen language.
Defines Token class and all token types.
"""

from dataclasses import dataclass
from typing import Any, Optional


class TokenType:
    """All token types in Zen language."""
    
    # Special tokens
    EOF = 'EOF'
    ILLEGAL = 'ILLEGAL'
    
    # Identifiers and literals
    IDENT = 'IDENT'        # variable names, function names, etc.
    INT = 'INT'            # integer literals
    STRING = 'STRING'      # string literals
    
    # Keywords
    BAG = 'BAG'            # package declaration
    LOAD = 'LOAD'          # import statement
    FX = 'FX'              # function declaration
    CLX = 'CLX'            # class declaration
    RETURN = 'RETURN'      # return statement
    IF = 'IF'              # conditional (future)
    ELSE = 'ELSE'          # conditional (future)
    FOR = 'FOR'            # loop (future)
    TRUE = 'TRUE'          # boolean true
    FALSE = 'FALSE'        # boolean false
    NIL = 'NIL'            # null value
    SELF = 'SELF'          # class instance reference
    
    # Operators
    ASSIGN = 'ASSIGN'      # =
    PLUS = 'PLUS'          # +
    MINUS = 'MINUS'        # -
    MULTIPLY = 'MULTIPLY'  # *
    DIVIDE = 'DIVIDE'      # /
    
    # Comparison operators
    EQ = 'EQ'              # ==
    NEQ = 'NEQ'            # !=
    LT = 'LT'              # <
    GT = 'GT'              # >
    LTE = 'LTE'            # <=
    GTE = 'GTE'            # >=
    
    # Logical operators
    AND = 'AND'            # &&
    OR = 'OR'              # ||
    NOT = 'NOT'            # !
    
    # Delimiters
    LPAREN = 'LPAREN'      # (
    RPAREN = 'RPAREN'      # )
    LBRACE = 'LBRACE'      # {
    RBRACE = 'RBRACE'      # }
    COMMA = 'COMMA'        # ,
    DOT = 'DOT'            # .


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
    literal: Any
    line: int = 1
    column: int = 1
    
    def __repr__(self) -> str:
        return f"Token({self.type}, {repr(self.literal)})"
    
    def __str__(self) -> str:
        return self.__repr__()


def lookup_ident(ident: str) -> str:
    """Look up identifier to see if it's a keyword."""
    return KEYWORDS.get(ident, TokenType.IDENT) 