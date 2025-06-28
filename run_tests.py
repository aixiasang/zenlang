"""
Test runner for the Zen language interpreter.
"""

import sys
import os
import unittest

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run tests
from tests.test_lexer import TestLexer

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add lexer tests
    suite.addTests(loader.loadTestsFromTestCase(TestLexer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite) 