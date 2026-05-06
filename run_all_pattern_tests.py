"""
Test Runner for Shelfly Design Patterns
========================================

This file runs all test cases for all 5 design patterns:
- Strategy Pattern
- Observer Pattern
- Factory Pattern
- Repository Pattern
- Singleton Pattern

Usage:
    python run_all_pattern_tests.py
"""

import os
import sys
import django

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelfly.settings')

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
django.setup()

# Now import Django test utilities
from django.test.utils import get_runner
from django.conf import settings


def main():
    """Run all tests for the project."""
    
    print("=" * 60)
    print("SHELFLY DESIGN PATTERNS - TEST RUNNER")
    print("=" * 60)
    print()
    
    # Get Django test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    
    # Run all tests in bookstore app
    result = test_runner.run_tests(['bookstore.tests'])
    
    print()
    print("=" * 60)
    if result == 0:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"❌ {result} TEST(S) FAILED!")
    print("=" * 60)
    
    return result


if __name__ == '__main__':
    sys.exit(main())