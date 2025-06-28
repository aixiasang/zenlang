#!/usr/bin/env python3
"""
Zen Language REPL (Read-Eval-Print Loop)
Interactive interpreter for the Zen programming language.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, LexerError
from parser import Parser
from evaluator import Evaluator, eval_node
from object import Environment, Error, NIL


class ZenREPL:
    """Read-Eval-Print Loop for Zen language."""
    
    def __init__(self):
        """Initialize the REPL."""
        self.evaluator = Evaluator()
        self.environment = Environment()
        
        # Setup global environment with built-ins
        for name, builtin in self.evaluator.globals.items():
            self.environment.set(name, builtin)
        
        self.prompt = "zen> "
        self.continuation_prompt = ".... "
    
    def run(self):
        """Run the REPL."""
        print("Zen Language Interpreter v0.1")
        print("Type 'exit()' or press Ctrl+C to quit")
        print("Type 'help' for help")
        print()
        
        while True:
            try:
                # Read input
                source = self._read_input()
                if source.strip() == "":
                    continue
                
                # Handle special commands
                if source.strip() in ["exit()", "quit()", "exit", "quit"]:
                    print("Goodbye!")
                    break
                elif source.strip() == "help":
                    self._show_help()
                    continue
                elif source.strip() == "env":
                    self._show_environment()
                    continue
                
                # Evaluate
                result = self._evaluate(source)
                
                # Print result (unless it's NIL)
                if result and result is not NIL:
                    print(result.inspect())
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"REPL Error: {e}")
    
    def _read_input(self):
        """Read input from user, handling multi-line expressions."""
        lines = []
        prompt = self.prompt
        
        while True:
            try:
                line = input(prompt)
                lines.append(line)
                
                # Check if we need more input (simple heuristic)
                joined = " ".join(lines).strip()
                if self._is_complete_expression(joined):
                    return joined
                else:
                    prompt = self.continuation_prompt
            except KeyboardInterrupt:
                raise
            except EOFError:
                raise
    
    def _is_complete_expression(self, source):
        """Check if the expression is complete (simple heuristic)."""
        if not source:
            return True
        
        # Count braces
        open_braces = source.count('{')
        close_braces = source.count('}')
        
        # Count parentheses
        open_parens = source.count('(')
        close_parens = source.count(')')
        
        # If braces/parens are balanced, expression is likely complete
        return open_braces == close_braces and open_parens == close_parens
    
    def _evaluate(self, source):
        """Evaluate Zen source code."""
        try:
            # Tokenize
            lexer = Lexer(source)
            
            # Parse
            parser = Parser(lexer)
            program = parser.parse_program()
            
            # Check for parse errors
            if parser.errors:
                for error in parser.errors:
                    print(f"Parse Error: {error}")
                return None
            
            # Evaluate
            result = eval_node(program, self.environment)
            
            if isinstance(result, Error):
                print(f"Runtime Error: {result.message}")
                return None
            
            return result
            
        except LexerError as e:
            print(f"Lexer Error: {e}")
            return None
        except Exception as e:
            print(f"Evaluation Error: {e}")
            return None
    
    def _show_help(self):
        """Show help information."""
        print("""
Zen Language REPL Help
======================

Basic usage:
  - Type any Zen expression and press Enter
  - Multi-line expressions are supported

Special commands:
  help      - Show this help
  env       - Show current environment (variables)
  exit()    - Exit the REPL
  quit()    - Exit the REPL

Examples:
  zen> 5 + 3
  8
  
  zen> name = "Alice"
  "Alice"
  
  zen> fx greet(name) { return "Hello, " + name }
  fx greet(name) { ... }
  
  zen> greet("World")
  "Hello, World"

Built-in functions:
  print(...)  - Print values
  len(str)    - Get string length
  type(obj)   - Get object type
  str(obj)    - Convert to string
  int(obj)    - Convert to integer
  bool(obj)   - Convert to boolean
""")
    
    def _show_environment(self):
        """Show current environment variables."""
        print("Current Environment:")
        print("===================")
        
        vars_shown = 0
        for name, value in self.environment.items():
            # Skip built-in functions for brevity
            if not hasattr(value, 'fn'):
                print(f"  {name} = {value.inspect()}")
                vars_shown += 1
        
        if vars_shown == 0:
            print("  (no user-defined variables)")
        
        print()


def run_file(filename):
    """Run a Zen file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        evaluator = Evaluator()
        environment = Environment()
        
        # Setup global environment
        for name, builtin in evaluator.globals.items():
            environment.set(name, builtin)
        
        # Tokenize and parse
        lexer = Lexer(source)
        parser = Parser(lexer)
        program = parser.parse_program()
        
        # Check for parse errors
        if parser.errors:
            print("Parse Errors:")
            for error in parser.errors:
                print(f"  {error}")
            return False
        
        # Evaluate
        result = eval_node(program, environment)
        
        if isinstance(result, Error):
            print(f"Runtime Error: {result.message}")
            return False
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return False
    except Exception as e:
        print(f"Error running file: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Run file
        filename = sys.argv[1]
        success = run_file(filename)
        sys.exit(0 if success else 1)
    else:
        # Start REPL
        repl = ZenREPL()
        repl.run()


if __name__ == "__main__":
    main() 