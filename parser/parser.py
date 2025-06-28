"""
Parser module for Zen language.
Implements a Pratt parser (operator precedence parser).
"""

from typing import List, Dict, Callable, Optional
from enum import IntEnum

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from lexer.lexer import Token, TokenType
from zen_ast import *


# Operator precedence levels
class Precedence(IntEnum):
    LOWEST = 1
    ASSIGN = 2      # =
    OR = 3          # ||
    AND = 4         # &&
    EQUALS = 5      # ==, !=
    LESSGREATER = 6 # >, <, >=, <=
    SUM = 7         # +, -
    PRODUCT = 8     # *, /
    PREFIX = 9      # -X, !X
    CALL = 10       # myFunction(X)
    INDEX = 11      # array[index], obj.member


# Precedence table
PRECEDENCES = {
    TokenType.ASSIGN: Precedence.ASSIGN,
    TokenType.OR: Precedence.OR,
    TokenType.AND: Precedence.AND,
    TokenType.EQ: Precedence.EQUALS,
    TokenType.NEQ: Precedence.EQUALS,
    TokenType.LT: Precedence.LESSGREATER,
    TokenType.GT: Precedence.LESSGREATER,
    TokenType.LTE: Precedence.LESSGREATER,
    TokenType.GTE: Precedence.LESSGREATER,
    TokenType.PLUS: Precedence.SUM,
    TokenType.MINUS: Precedence.SUM,
    TokenType.MULTIPLY: Precedence.PRODUCT,
    TokenType.DIVIDE: Precedence.PRODUCT,
    TokenType.LPAREN: Precedence.CALL,
    TokenType.DOT: Precedence.INDEX,
}


class Parser:
    """Pratt parser for Zen language."""
    
    def __init__(self, lexer: Lexer):
        """Initialize parser with a lexer."""
        self.lexer = lexer
        self.tokens = list(lexer.get_tokens())
        self.current_pos = 0
        self.errors: List[str] = []
        
        # Pratt parser maps
        self.prefix_parse_fns: Dict[str, Callable] = {}
        self.infix_parse_fns: Dict[str, Callable] = {}
        
        # Register prefix parsers
        self._register_prefix(TokenType.IDENT, self._parse_identifier)
        self._register_prefix(TokenType.INT, self._parse_integer_literal)
        self._register_prefix(TokenType.STRING, self._parse_string_literal)
        self._register_prefix(TokenType.TRUE, self._parse_boolean_literal)
        self._register_prefix(TokenType.FALSE, self._parse_boolean_literal)
        self._register_prefix(TokenType.NIL, self._parse_nil_literal)
        self._register_prefix(TokenType.SELF, self._parse_self_expression)
        self._register_prefix(TokenType.MINUS, self._parse_prefix_expression)
        self._register_prefix(TokenType.NOT, self._parse_prefix_expression)
        self._register_prefix(TokenType.LPAREN, self._parse_grouped_expression)
        
        # Register infix parsers
        for op in [TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
                   TokenType.EQ, TokenType.NEQ, TokenType.LT, TokenType.GT, 
                   TokenType.LTE, TokenType.GTE, TokenType.AND, TokenType.OR]:
            self._register_infix(op, self._parse_infix_expression)
        
        self._register_infix(TokenType.LPAREN, self._parse_call_expression)
        self._register_infix(TokenType.DOT, self._parse_member_access_expression)
    
    def _register_prefix(self, token_type: str, fn: Callable):
        """Register a prefix parse function."""
        self.prefix_parse_fns[token_type] = fn
    
    def _register_infix(self, token_type: str, fn: Callable):
        """Register an infix parse function."""
        self.infix_parse_fns[token_type] = fn
    
    def _current_token(self) -> Optional[Token]:
        """Get current token."""
        if self.current_pos < len(self.tokens):
            return self.tokens[self.current_pos]
        return None
    
    def _peek_token(self) -> Optional[Token]:
        """Peek at next token."""
        if self.current_pos + 1 < len(self.tokens):
            return self.tokens[self.current_pos + 1]
        return None
    
    def _advance(self):
        """Move to next token."""
        if self.current_pos < len(self.tokens):
            self.current_pos += 1
    
    def _current_token_is(self, token_type: str) -> bool:
        """Check if current token is of given type."""
        token = self._current_token()
        return token and token.type == token_type
    
    def _peek_token_is(self, token_type: str) -> bool:
        """Check if next token is of given type."""
        token = self._peek_token()
        return token and token.type == token_type
    
    def _expect_peek(self, token_type: str) -> bool:
        """Check if next token is expected type and advance if so."""
        if self._peek_token_is(token_type):
            self._advance()
            return True
        else:
            self._peek_error(token_type)
            return False
    
    def _peek_error(self, token_type: str):
        """Add peek error to errors list."""
        peek = self._peek_token()
        if peek:
            msg = f"Expected next token to be {token_type}, got {peek.type} instead"
        else:
            msg = f"Expected next token to be {token_type}, but reached EOF"
        self.errors.append(msg)
    
    def _current_precedence(self) -> Precedence:
        """Get precedence of current token."""
        token = self._current_token()
        if token and token.type in PRECEDENCES:
            return PRECEDENCES[token.type]
        return Precedence.LOWEST
    
    def _peek_precedence(self) -> Precedence:
        """Get precedence of next token."""
        token = self._peek_token()
        if token and token.type in PRECEDENCES:
            return PRECEDENCES[token.type]
        return Precedence.LOWEST
    
    def parse_program(self) -> Program:
        """Parse the entire program."""
        statements = []
        
        while not self._current_token_is(TokenType.EOF):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._advance()
        
        return Program(statements=statements)
    
    def _parse_statement(self) -> Optional[Statement]:
        """Parse a statement."""
        token = self._current_token()
        if not token:
            return None
        
        # Check statement type
        if token.type == TokenType.BAG:
            return self._parse_package_statement()
        elif token.type == TokenType.LOAD:
            return self._parse_load_statement()
        elif token.type == TokenType.FX:
            return self._parse_function_statement()
        elif token.type == TokenType.CLX:
            return self._parse_class_statement()
        elif token.type == TokenType.RETURN:
            return self._parse_return_statement()
        elif token.type == TokenType.LBRACE:
            return self._parse_block_statement()
        else:
            # Try to parse assignment or expression statement
            return self._parse_assignment_or_expression_statement()
    
    def _parse_package_statement(self) -> Optional[PackageStatement]:
        """Parse package statement: bag name"""
        if not self._expect_peek(TokenType.IDENT):
            return None
        
        name = self._current_token().literal
        return PackageStatement(name=name)
    
    def _parse_load_statement(self) -> Optional[LoadStatement]:
        """Parse load statement: load("path1", "path2", ...)"""
        if not self._expect_peek(TokenType.LPAREN):
            return None
        
        imports = []
        
        # We're already at LPAREN, advance past it
        self._advance()
        
        # Check for empty imports
        if self._current_token_is(TokenType.RPAREN):
            return LoadStatement(imports=imports)
        
        # Parse imports
        while True:
            if self._current_token_is(TokenType.STRING):
                imports.append(self._current_token().literal)
                
                if self._peek_token_is(TokenType.COMMA):
                    self._advance()  # Move to comma
                    self._advance()  # Move past comma
                elif self._peek_token_is(TokenType.RPAREN):
                    self._advance()  # Move to )
                    break
                else:
                    self.errors.append("Expected , or ) after import path")
                    break
            else:
                self.errors.append("Expected string literal in load statement")
                break
        
        return LoadStatement(imports=imports)
    
    def _parse_function_statement(self) -> Optional[FunctionStatement]:
        """Parse function statement: fx name(params) { body }"""
        if not self._expect_peek(TokenType.IDENT):
            return None
        
        name = self._current_token().literal
        
        if not self._expect_peek(TokenType.LPAREN):
            return None
        
        parameters = self._parse_function_parameters()
        
        if not self._expect_peek(TokenType.LBRACE):
            return None
        
        body = self._parse_block_statement()
        
        return FunctionStatement(name=name, parameters=parameters, body=body)
    
    def _parse_function_parameters(self) -> List[str]:
        """Parse function parameters."""
        params = []
        
        # We're already at the LPAREN, so advance past it
        self._advance()
        
        # Check for empty parameter list
        if self._current_token_is(TokenType.RPAREN):
            return params
        
        while True:
            if self._current_token_is(TokenType.IDENT):
                params.append(self._current_token().literal)
                
                # Check if there's a comma (more parameters)
                if self._peek_token_is(TokenType.COMMA):
                    self._advance()  # Move to comma
                    self._advance()  # Move past comma
                elif self._peek_token_is(TokenType.RPAREN):
                    self._advance()  # Move to )
                    break
                else:
                    self.errors.append("Expected , or ) after parameter")
                    break
            else:
                self.errors.append("Expected parameter name")
                break
        
        return params
    
    def _parse_class_statement(self) -> Optional[ClassStatement]:
        """Parse class statement: clx name { methods }"""
        if not self._expect_peek(TokenType.IDENT):
            return None
        
        name = self._current_token().literal
        
        if not self._expect_peek(TokenType.LBRACE):
            return None
        
        methods = []
        
        # Skip opening brace
        self._advance()
        
        while not self._current_token_is(TokenType.RBRACE) and not self._current_token_is(TokenType.EOF):
            if self._current_token_is(TokenType.FX):
                method = self._parse_function_statement()
                if method:
                    methods.append(method)
            self._advance()
        
        return ClassStatement(name=name, methods=methods)
    
    def _parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        # Skip 'return'
        self._advance()
        
        # Check if there's a return value
        if self._current_token_is(TokenType.RBRACE) or self._current_token_is(TokenType.EOF):
            return ReturnStatement(value=None)
        
        value = self._parse_expression(Precedence.LOWEST)
        return ReturnStatement(value=value)
    
    def _parse_block_statement(self) -> BlockStatement:
        """Parse block statement: { statements }"""
        statements = []
        
        # Skip opening brace
        self._advance()
        
        while not self._current_token_is(TokenType.RBRACE) and not self._current_token_is(TokenType.EOF):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
            self._advance()
        
        return BlockStatement(statements=statements)
    
    def _parse_assignment_or_expression_statement(self) -> Optional[Statement]:
        """Parse assignment or expression statement."""
        # Try to parse as expression first
        expr = self._parse_expression(Precedence.LOWEST)
        if not expr:
            return None
        
        # Check if it's an assignment
        if self._peek_token_is(TokenType.ASSIGN):
            # It's an assignment
            self._advance()  # Move to =
            self._advance()  # Move past =
            
            value = self._parse_expression(Precedence.LOWEST)
            if not value:
                return None
            
            return AssignStatement(target=expr, value=value)
        else:
            # It's just an expression statement
            return ExpressionStatement(expression=expr)
    
    def _parse_expression(self, precedence: Precedence) -> Optional[Expression]:
        """Parse expression using Pratt parsing."""
        token = self._current_token()
        if not token or token.type not in self.prefix_parse_fns:
            self.errors.append(f"No prefix parse function for {token.type if token else 'EOF'}")
            return None
        
        prefix_fn = self.prefix_parse_fns[token.type]
        left_expr = prefix_fn()
        
        while not self._peek_token_is(TokenType.EOF) and precedence < self._peek_precedence():
            peek = self._peek_token()
            if not peek or peek.type not in self.infix_parse_fns:
                return left_expr
            
            self._advance()
            infix_fn = self.infix_parse_fns[peek.type]
            left_expr = infix_fn(left_expr)
        
        return left_expr
    
    # Prefix parse functions
    def _parse_identifier(self) -> Identifier:
        """Parse identifier."""
        return Identifier(value=self._current_token().literal)
    
    def _parse_integer_literal(self) -> IntegerLiteral:
        """Parse integer literal."""
        return IntegerLiteral(value=self._current_token().literal)
    
    def _parse_string_literal(self) -> StringLiteral:
        """Parse string literal."""
        return StringLiteral(value=self._current_token().literal)
    
    def _parse_boolean_literal(self) -> BooleanLiteral:
        """Parse boolean literal."""
        return BooleanLiteral(value=self._current_token().type == TokenType.TRUE)
    
    def _parse_nil_literal(self) -> NilLiteral:
        """Parse nil literal."""
        return NilLiteral()
    
    def _parse_self_expression(self) -> SelfExpression:
        """Parse self expression."""
        return SelfExpression()
    
    def _parse_prefix_expression(self) -> Optional[PrefixExpression]:
        """Parse prefix expression."""
        operator = self._current_token().literal
        
        self._advance()
        right = self._parse_expression(Precedence.PREFIX)
        
        if not right:
            return None
        
        return PrefixExpression(operator=operator, right=right)
    
    def _parse_grouped_expression(self) -> Optional[Expression]:
        """Parse grouped expression: (expression)"""
        self._advance()  # Skip (
        
        expr = self._parse_expression(Precedence.LOWEST)
        
        if not self._expect_peek(TokenType.RPAREN):
            return None
        
        return expr
    
    # Infix parse functions
    def _parse_infix_expression(self, left: Expression) -> InfixExpression:
        """Parse infix expression."""
        operator = self._current_token().literal
        precedence = self._current_precedence()
        
        self._advance()
        right = self._parse_expression(precedence)
        
        return InfixExpression(left=left, operator=operator, right=right)
    
    def _parse_call_expression(self, function: Expression) -> CallExpression:
        """Parse call expression."""
        arguments = []
        
        # We're already at LPAREN, advance past it
        self._advance()
        
        # Check for empty argument list
        if self._current_token_is(TokenType.RPAREN):
            return CallExpression(function=function, arguments=arguments)
        
        while True:
            arg = self._parse_expression(Precedence.LOWEST)
            if arg:
                arguments.append(arg)
                
                if self._peek_token_is(TokenType.COMMA):
                    self._advance()  # Move to comma
                    self._advance()  # Move past comma
                elif self._peek_token_is(TokenType.RPAREN):
                    self._advance()  # Move to )
                    break
                else:
                    self.errors.append("Expected , or ) after argument")
                    break
            else:
                break
        
        return CallExpression(function=function, arguments=arguments)
    
    def _parse_member_access_expression(self, object: Expression) -> Optional[MemberAccessExpression]:
        """Parse member access expression."""
        self._advance()  # Skip .
        
        if not self._current_token_is(TokenType.IDENT):
            self.errors.append("Expected identifier after .")
            return None
        
        member = self._current_token().literal
        return MemberAccessExpression(object=object, member=member) 