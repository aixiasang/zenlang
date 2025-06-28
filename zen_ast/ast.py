"""
AST (Abstract Syntax Tree) module for Zen language.
Defines all AST node types for the language.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dataclasses import dataclass


# Base interfaces
class Node(ABC):
    """Base interface for all AST nodes."""
    
    @abstractmethod
    def token_literal(self) -> str:
        """Return the literal value of the token that started this node."""
        pass
    
    @abstractmethod
    def string(self) -> str:
        """Return a string representation of the node for debugging."""
        pass


class Statement(Node):
    """Base interface for all statement nodes."""
    pass


class Expression(Node):
    """Base interface for all expression nodes."""
    pass


# Program (root node)
@dataclass
class Program(Node):
    """The root node of every AST - represents the entire program."""
    statements: List[Statement]
    
    def token_literal(self) -> str:
        if self.statements:
            return self.statements[0].token_literal()
        return ""
    
    def string(self) -> str:
        return "\n".join(stmt.string() for stmt in self.statements)


# Statement types
@dataclass
class PackageStatement(Statement):
    """Package declaration: bag <name>"""
    name: str
    
    def token_literal(self) -> str:
        return "bag"
    
    def string(self) -> str:
        return f"bag {self.name}"


@dataclass
class LoadStatement(Statement):
    """Import statement: load("path1", "path2", ...)"""
    imports: List[str]
    
    def token_literal(self) -> str:
        return "load"
    
    def string(self) -> str:
        imports_str = ", ".join(f'"{imp}"' for imp in self.imports)
        return f"load({imports_str})"


@dataclass
class FunctionStatement(Statement):
    """Function declaration: fx name(params) { body }"""
    name: str
    parameters: List[str]
    body: 'BlockStatement'
    
    def token_literal(self) -> str:
        return "fx"
    
    def string(self) -> str:
        params = ", ".join(self.parameters)
        return f"fx {self.name}({params}) {self.body.string()}"


@dataclass
class ClassStatement(Statement):
    """Class declaration: clx name { methods }"""
    name: str
    methods: List[FunctionStatement]
    
    def token_literal(self) -> str:
        return "clx"
    
    def string(self) -> str:
        methods_str = "\n".join(method.string() for method in self.methods)
        return f"clx {self.name} {{\n{methods_str}\n}}"


@dataclass
class ReturnStatement(Statement):
    """Return statement: return expression"""
    value: Optional[Expression] = None
    
    def token_literal(self) -> str:
        return "return"
    
    def string(self) -> str:
        if self.value:
            return f"return {self.value.string()}"
        return "return"


@dataclass
class ExpressionStatement(Statement):
    """A statement consisting of a single expression."""
    expression: Expression
    
    def token_literal(self) -> str:
        return self.expression.token_literal()
    
    def string(self) -> str:
        return self.expression.string()


@dataclass
class AssignStatement(Statement):
    """Assignment statement: name = expression or obj.field = expression"""
    target: Expression  # Can be Identifier or MemberAccessExpression
    value: Expression
    
    def token_literal(self) -> str:
        return self.target.token_literal()
    
    def string(self) -> str:
        return f"{self.target.string()} = {self.value.string()}"


@dataclass
class BlockStatement(Statement):
    """Block statement: { statements }"""
    statements: List[Statement]
    
    def token_literal(self) -> str:
        return "{"
    
    def string(self) -> str:
        stmt_strings = [stmt.string() for stmt in self.statements]
        return "{\n" + "\n".join(stmt_strings) + "\n}"


# Expression types
@dataclass
class Identifier(Expression):
    """Identifier expression: variable names, function names, etc."""
    value: str
    
    def token_literal(self) -> str:
        return self.value
    
    def string(self) -> str:
        return self.value


@dataclass
class IntegerLiteral(Expression):
    """Integer literal expression: 42, 123, etc."""
    value: int
    
    def token_literal(self) -> str:
        return str(self.value)
    
    def string(self) -> str:
        return str(self.value)


@dataclass
class StringLiteral(Expression):
    """String literal expression: "hello", etc."""
    value: str
    
    def token_literal(self) -> str:
        return f'"{self.value}"'
    
    def string(self) -> str:
        return f'"{self.value}"'


@dataclass
class BooleanLiteral(Expression):
    """Boolean literal expression: true, false"""
    value: bool
    
    def token_literal(self) -> str:
        return "true" if self.value else "false"
    
    def string(self) -> str:
        return "true" if self.value else "false"


@dataclass
class NilLiteral(Expression):
    """Nil literal expression: nil"""
    
    def token_literal(self) -> str:
        return "nil"
    
    def string(self) -> str:
        return "nil"


@dataclass
class SelfExpression(Expression):
    """Self expression: self"""
    
    def token_literal(self) -> str:
        return "self"
    
    def string(self) -> str:
        return "self"


@dataclass
class PrefixExpression(Expression):
    """Prefix expression: -5, !true, etc."""
    operator: str
    right: Expression
    
    def token_literal(self) -> str:
        return self.operator
    
    def string(self) -> str:
        return f"({self.operator}{self.right.string()})"


@dataclass
class InfixExpression(Expression):
    """Infix expression: 5 + 5, a > b, etc."""
    left: Expression
    operator: str
    right: Expression
    
    def token_literal(self) -> str:
        return self.operator
    
    def string(self) -> str:
        return f"({self.left.string()} {self.operator} {self.right.string()})"


@dataclass
class CallExpression(Expression):
    """Function call expression: add(1, 2), Person("Alice", 30)"""
    function: Expression  # Can be Identifier, MemberAccessExpression, or even another CallExpression
    arguments: List[Expression]
    
    def token_literal(self) -> str:
        return "("
    
    def string(self) -> str:
        args = ", ".join(arg.string() for arg in self.arguments)
        return f"{self.function.string()}({args})"


@dataclass
class MemberAccessExpression(Expression):
    """Member access expression: obj.field, obj.method"""
    object: Expression
    member: str
    
    def token_literal(self) -> str:
        return "."
    
    def string(self) -> str:
        return f"{self.object.string()}.{self.member}" 