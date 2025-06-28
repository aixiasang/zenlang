"""
Environment module for Zen language.
Manages variable bindings and scoping.
"""

from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .object import Object


class Environment:
    """
    Environment for variable bindings.
    
    Supports nested scopes through the outer environment reference.
    This enables lexical scoping and closures.
    """
    
    def __init__(self, outer: Optional['Environment'] = None):
        """
        Initialize environment.
        
        Args:
            outer: Parent environment for nested scoping
        """
        self.store: Dict[str, 'Object'] = {}
        self.outer = outer
    
    def get(self, name: str) -> Optional['Object']:
        """
        Get a variable value.
        
        Searches current environment first, then outer environments.
        
        Args:
            name: Variable name
            
        Returns:
            Object value or None if not found
        """
        if name in self.store:
            return self.store[name]
        elif self.outer is not None:
            return self.outer.get(name)
        else:
            return None
    
    def set(self, name: str, value: 'Object'):
        """
        Set a variable value in current environment.
        
        Args:
            name: Variable name
            value: Object value
        """
        self.store[name] = value
    
    def update(self, name: str, value: 'Object') -> bool:
        """
        Update an existing variable in any scope.
        
        Searches for the variable in current and outer environments
        and updates it where found. If not found, creates in current scope.
        
        Args:
            name: Variable name
            value: New value
            
        Returns:
            True if variable was found and updated, False if created new
        """
        if name in self.store:
            self.store[name] = value
            return True
        elif self.outer is not None and self.outer.has(name):
            return self.outer.update(name, value)
        else:
            # Variable doesn't exist, create in current scope
            self.store[name] = value
            return False
    
    def has(self, name: str) -> bool:
        """
        Check if variable exists in current or outer environments.
        
        Args:
            name: Variable name
            
        Returns:
            True if variable exists
        """
        return name in self.store or (self.outer is not None and self.outer.has(name))
    
    def define(self, name: str, value: 'Object'):
        """
        Define a variable in current environment.
        
        This always creates/overwrites in the current scope,
        regardless of whether the variable exists in outer scopes.
        
        Args:
            name: Variable name
            value: Object value
        """
        self.store[name] = value
    
    def keys(self):
        """Get all variable names in current environment."""
        return self.store.keys()
    
    def items(self):
        """Get all (name, value) pairs in current environment."""
        return self.store.items()
    
    def copy(self) -> 'Environment':
        """
        Create a shallow copy of this environment.
        
        The outer reference is preserved, but the store is copied.
        """
        new_env = Environment(self.outer)
        new_env.store = self.store.copy()
        return new_env
    
    def new_enclosed_environment(self) -> 'Environment':
        """
        Create a new environment with this one as the outer environment.
        
        This is useful for function calls and block scopes.
        """
        return Environment(outer=self)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        vars_info = ", ".join(f"{k}={v.inspect() if hasattr(v, 'inspect') else str(v)}" 
                             for k, v in self.store.items())
        outer_info = " -> outer" if self.outer else ""
        return f"Environment({{{vars_info}}}{outer_info})"
    
    def debug_print(self, level: int = 0):
        """Print environment hierarchy for debugging."""
        indent = "  " * level
        print(f"{indent}Environment level {level}:")
        for name, value in self.store.items():
            value_str = value.inspect() if hasattr(value, 'inspect') else str(value)
            print(f"{indent}  {name} = {value_str}")
        
        if self.outer:
            self.outer.debug_print(level + 1) 