"""
Object system for Zen language runtime.
Defines all types that can exist during program execution.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass


class ObjectType:
    """Runtime object type constants."""
    INTEGER = "INTEGER"
    STRING = "STRING" 
    BOOLEAN = "BOOLEAN"
    NIL = "NIL"
    RETURN_VALUE = "RETURN_VALUE"
    ERROR = "ERROR"
    FUNCTION = "FUNCTION"
    CLASS = "CLASS"
    INSTANCE = "INSTANCE"
    BUILTIN = "BUILTIN"
    MODULE = "MODULE"


class Object(ABC):
    """Base class for all runtime objects."""
    
    @abstractmethod
    def type(self) -> str:
        """Return the type of this object."""
        pass
    
    @abstractmethod
    def inspect(self) -> str:
        """Return string representation for debugging."""
        pass
    
    def is_truthy(self) -> bool:
        """Determine if object is truthy in boolean context."""
        return True  # Most objects are truthy by default


@dataclass
class Integer(Object):
    """Integer object."""
    value: int
    
    def type(self) -> str:
        return ObjectType.INTEGER
    
    def inspect(self) -> str:
        return str(self.value)
    
    def is_truthy(self) -> bool:
        return self.value != 0


@dataclass  
class String(Object):
    """String object."""
    value: str
    
    def type(self) -> str:
        return ObjectType.STRING
    
    def inspect(self) -> str:
        return f'"{self.value}"'
    
    def is_truthy(self) -> bool:
        return len(self.value) > 0


@dataclass
class Boolean(Object):
    """Boolean object."""
    value: bool
    
    def type(self) -> str:
        return ObjectType.BOOLEAN
    
    def inspect(self) -> str:
        return "true" if self.value else "false"
    
    def is_truthy(self) -> bool:
        return self.value


class Nil(Object):
    """Nil/null object - singleton."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def type(self) -> str:
        return ObjectType.NIL
    
    def inspect(self) -> str:
        return "nil"
    
    def is_truthy(self) -> bool:
        return False


@dataclass
class ReturnValue(Object):
    """Wrapper for return values to control execution flow."""
    value: Object
    
    def type(self) -> str:
        return ObjectType.RETURN_VALUE
    
    def inspect(self) -> str:
        return self.value.inspect()


@dataclass
class Error(Object):
    """Error object."""
    message: str
    
    def type(self) -> str:
        return ObjectType.ERROR
    
    def inspect(self) -> str:
        return f"ERROR: {self.message}"
    
    def is_truthy(self) -> bool:
        return False


@dataclass
class Function(Object):
    """Function object with closure support."""
    parameters: List[str]
    body: Any  # AST BlockStatement
    env: 'Environment'  # Closure environment
    name: str = ""
    
    def type(self) -> str:
        return ObjectType.FUNCTION
    
    def inspect(self) -> str:
        params = ", ".join(self.parameters)
        name_part = f"{self.name}" if self.name else "<anonymous>"
        return f"fx {name_part}({params}) {{ ... }}"


@dataclass
class Class(Object):
    """Class object."""
    name: str
    methods: Dict[str, Function]
    
    def type(self) -> str:
        return ObjectType.CLASS
    
    def inspect(self) -> str:
        method_names = list(self.methods.keys())
        return f"clx {self.name} {{ {', '.join(method_names)} }}"
    
    def get_method(self, name: str) -> Optional[Function]:
        """Get a method by name."""
        return self.methods.get(name)
    
    def has_method(self, name: str) -> bool:
        """Check if class has a method."""
        return name in self.methods


@dataclass
class Instance(Object):
    """Instance of a class."""
    cls: Class
    fields: 'Environment'  # Instance variables
    
    def type(self) -> str:
        return ObjectType.INSTANCE
    
    def inspect(self) -> str:
        return f"<{self.cls.name} instance>"
    
    def get_field(self, name: str) -> Optional[Object]:
        """Get an instance field."""
        return self.fields.get(name)
    
    def set_field(self, name: str, value: Object):
        """Set an instance field."""
        self.fields.set(name, value)
    
    def get_method(self, name: str) -> Optional[Function]:
        """Get a method from the class."""
        return self.cls.get_method(name)


# Type for builtin functions
BuiltinFunction = Callable[..., Object]


@dataclass
class Builtin(Object):
    """Built-in function object."""
    fn: BuiltinFunction
    name: str = ""
    
    def type(self) -> str:
        return ObjectType.BUILTIN
    
    def inspect(self) -> str:
        return f"<builtin function {self.name}>"


@dataclass
class Module(Object):
    """Module object for package system."""
    name: str
    path: str
    env: 'Environment'  # Module's public namespace
    private_env: 'Environment'  # Module's complete namespace (including private)
    package_name: str = ""  # Package name declared with 'bag'
    
    def type(self) -> str:
        return ObjectType.MODULE
    
    def inspect(self) -> str:
        return f"<module {self.name}>"
    
    def get_member(self, name: str) -> Optional[Object]:
        """Get a public member from the module."""
        return self.env.get(name)
    
    def get_private_member(self, name: str) -> Optional[Object]:
        """Get any member from the module (for internal use)."""
        return self.private_env.get(name)
    
    def is_public(self, name: str) -> bool:
        """Check if a name is public (starts with uppercase)."""
        return name and name[0].isupper()
    
    def get_public_members(self) -> Dict[str, Object]:
        """Get all public members."""
        public_members = {}
        for name, obj in self.private_env.items():
            if self.is_public(name):
                public_members[name] = obj
        return public_members


class ModuleManager:
    """Manages module loading and caching."""
    
    def __init__(self):
        self.loaded_modules: Dict[str, Module] = {}
        self.loading_stack: List[str] = []  # For circular import detection
        self.search_paths: List[str] = [
            ".",  # Current directory
            "./examples",  # Examples directory
            "./lib",  # Local lib directory
            "./modules",  # Local modules directory
        ]
    
    def is_loading(self, path: str) -> bool:
        """Check if a module is currently being loaded (circular import detection)."""
        return path in self.loading_stack
    
    def start_loading(self, path: str):
        """Mark a module as being loaded."""
        self.loading_stack.append(path)
    
    def finish_loading(self, path: str):
        """Mark a module as finished loading."""
        if path in self.loading_stack:
            self.loading_stack.remove(path)
    
    def get_cached_module(self, path: str) -> Optional[Module]:
        """Get a cached module."""
        return self.loaded_modules.get(path)
    
    def cache_module(self, path: str, module: Module):
        """Cache a loaded module."""
        self.loaded_modules[path] = module
    
    def resolve_module_path(self, module_path: str, current_dir: str = ".") -> Optional[str]:
        """Resolve module path to actual file path."""
        import os
        
        # If it's already a .zen file, use as-is
        if module_path.endswith('.zen'):
            test_paths = [module_path]
        else:
            # Try different extensions and patterns
            test_paths = [
                f"{module_path}.zen",
                f"{module_path}/main.zen",
                f"{module_path}/index.zen",
            ]
        
        # Search in all search paths
        all_search_paths = [current_dir] + self.search_paths
        
        for search_path in all_search_paths:
            for test_path in test_paths:
                full_path = os.path.join(search_path, test_path)
                if os.path.isfile(full_path):
                    return os.path.abspath(full_path)
        
        return None


# Global module manager instance
module_manager = ModuleManager()

# Singletons for commonly used objects
NIL = Nil()
TRUE = Boolean(True)
FALSE = Boolean(False)


def native_bool_to_boolean_object(input_bool: bool) -> Boolean:
    """Convert Python bool to Zen Boolean object."""
    return TRUE if input_bool else FALSE


def is_error(obj: Object) -> bool:
    """Check if object is an error."""
    return obj.type() == ObjectType.ERROR


def is_return_value(obj: Object) -> bool:
    """Check if object is a return value."""
    return obj.type() == ObjectType.RETURN_VALUE 