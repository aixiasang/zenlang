"""
Simple test script for the Zen lexer.
"""

# First, let's simplify the imports by including all code directly
import re
from dataclasses import dataclass
from typing import List, Any


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
    
    # Comparison operators (future)
    EQ = 'EQ'              # ==
    NEQ = 'NEQ'            # !=
    LT = 'LT'              # <
    GT = 'GT'              # >
    LTE = 'LTE'            # <=
    GTE = 'GTE'            # >=
    
    # Logical operators (future)
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


class Lexer:
    """Lexical analyzer for Zen language."""
    
    # Regular expression patterns for tokens
    TOKEN_PATTERNS = [
        # Comments (to be skipped)
        (r'//[^\n]*', None),  # Single-line comment
        (r'/\*[\s\S]*?\*/', None),  # Multi-line comment
        
        # Whitespace (to be skipped)
        (r'[ \t\r]+', None),  # Spaces, tabs, carriage returns
        (r'\n', 'NEWLINE'),  # Newline (track for line numbers)
        
        # String literals (must come before other patterns)
        (r'"([^"\\]|\\.)*"', TokenType.STRING),
        
        # Number literals
        (r'\d+', TokenType.INT),
        
        # Two-character operators
        (r'==', TokenType.EQ),
        (r'!=', TokenType.NEQ),
        (r'<=', TokenType.LTE),
        (r'>=', TokenType.GTE),
        (r'&&', TokenType.AND),
        (r'\|\|', TokenType.OR),
        
        # Single-character operators and delimiters
        (r'\+', TokenType.PLUS),
        (r'-', TokenType.MINUS),
        (r'\*', TokenType.MULTIPLY),
        (r'/', TokenType.DIVIDE),
        (r'=', TokenType.ASSIGN),
        (r'<', TokenType.LT),
        (r'>', TokenType.GT),
        (r'!', TokenType.NOT),
        (r'\(', TokenType.LPAREN),
        (r'\)', TokenType.RPAREN),
        (r'\{', TokenType.LBRACE),
        (r'\}', TokenType.RBRACE),
        (r',', TokenType.COMMA),
        (r'\.', TokenType.DOT),
        
        # Identifiers and keywords (must come after operators)
        (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENT_OR_KEYWORD'),
    ]
    
    # Compile patterns into a single regex
    MASTER_PATTERN = '|'.join(f'({pattern})' for pattern, _ in TOKEN_PATTERNS)
    MASTER_REGEX = re.compile(MASTER_PATTERN)
    
    def __init__(self, source: str):
        """Initialize lexer with source code."""
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self._tokenize()
    
    def _tokenize(self):
        """Tokenize the entire source code."""
        while self.position < len(self.source):
            # Try to match a token at current position
            match = self.MASTER_REGEX.match(self.source, self.position)
            
            if not match:
                # Illegal character
                char = self.source[self.position]
                self.tokens.append(Token(
                    type=TokenType.ILLEGAL,
                    literal=char,
                    line=self.line,
                    column=self.column
                ))
                self.position += 1
                self.column += 1
                continue
            
            # Find which pattern matched
            matched_text = match.group(0)
            token_type = None
            
            # Find which pattern matched by checking each group
            for i, (pattern, ttype) in enumerate(self.TOKEN_PATTERNS):
                group_index = i + 1
                try:
                    if match.group(group_index) == matched_text:
                        token_type = ttype
                        break
                except IndexError:
                    continue
            
            # Handle the matched token
            if token_type is None:
                # Skip whitespace and comments
                pass
            elif token_type == 'NEWLINE':
                # Update line and column counters
                self.line += 1
                self.column = 1
            elif token_type == 'IDENT_OR_KEYWORD':
                # Check if it's a keyword
                actual_type = lookup_ident(matched_text)
                self.tokens.append(Token(
                    type=actual_type,
                    literal=matched_text,
                    line=self.line,
                    column=self.column
                ))
            elif token_type == TokenType.STRING:
                # Remove quotes from string literal
                string_value = matched_text[1:-1]
                # Process escape sequences
                string_value = string_value.replace('\\n', '\n')
                string_value = string_value.replace('\\t', '\t')
                string_value = string_value.replace('\\r', '\r')
                string_value = string_value.replace('\\\\', '\\')
                string_value = string_value.replace('\\"', '"')
                self.tokens.append(Token(
                    type=TokenType.STRING,
                    literal=string_value,
                    line=self.line,
                    column=self.column
                ))
            elif token_type == TokenType.INT:
                # Convert to integer
                self.tokens.append(Token(
                    type=TokenType.INT,
                    literal=int(matched_text),
                    line=self.line,
                    column=self.column
                ))
            else:
                # Regular token
                self.tokens.append(Token(
                    type=token_type,
                    literal=matched_text,
                    line=self.line,
                    column=self.column
                ))
            
            # Update position and column
            self.position = match.end()
            if token_type != 'NEWLINE':
                self.column += len(matched_text)
        
        # Add EOF token
        self.tokens.append(Token(
            type=TokenType.EOF,
            literal=None,
            line=self.line,
            column=self.column
        ))
    
    def get_tokens(self) -> List[Token]:
        """Get all tokens."""
        return self.tokens
    
    def __iter__(self):
        """Make lexer iterable."""
        return iter(self.tokens)


# Simple test cases
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


def test_complex_program():
    """Test a complex Zen program."""
    print("Test 4: Complex Zen program")
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
    print("\nFirst 20 tokens:")
    for i, token in enumerate(tokens[:20]):
        print(f"  {i}: {token}")
    print()


if __name__ == "__main__":
    test_basic()
    test_comments()
    test_string_literals()
    test_complex_program()
    
    print("All tests completed!") 