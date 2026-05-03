"""
Direct Test Runner - Bypasses Django management command
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelfly.settings')
django.setup()

# Now import test modules
from bookstore.tests import (
    test_strategy_pattern,
    test_factory_pattern,
    test_repository_pattern,
    test_observer_pattern,
    test_singleton_pattern
)

import unittest

def run_tests():
    """Run all tests and display results."""
    
    print("=" * 80)
    print("RUNNING ALL DESIGN PATTERN TESTS")
    print("=" * 80)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules
    test_modules = [
        ('Strategy Pattern', test_strategy_pattern),
        ('Factory Pattern', test_factory_pattern),
        ('Repository Pattern', test_repository_pattern),
        ('Observer Pattern', test_observer_pattern),
        ('Singleton Pattern', test_singleton_pattern),
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    results_by_pattern = {}
    
    for pattern_name, module in test_modules:
        print(f"\n{'=' * 80}")
        print(f"Testing: {pattern_name}")
        print('=' * 80)
        
        # Load tests from module
        pattern_suite = loader.loadTestsFromModule(module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(pattern_suite)
        
        # Store results
        tests_run = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        passed = tests_run - failures - errors
        
        results_by_pattern[pattern_name] = {
            'total': tests_run,
            'passed': passed,
            'failed': failures,
            'errors': errors,
            'success': failures == 0 and errors == 0
        }
        
        total_tests += tests_run
        total_failures += failures
        total_errors += errors
        
        # Print summary for this pattern
        print(f"\n{pattern_name} Summary:")
        print(f"  Tests Run: {tests_run}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failures}")
        print(f"  Errors: {errors}")
        print(f"  Status: {'✅ PASS' if failures == 0 and errors == 0 else '❌ FAIL'}")
        
        # Print failure details if any
        if failures > 0:
            print(f"\n  Failures:")
            for test, traceback in result.failures:
                print(f"    - {test}")
                print(f"      {traceback[:200]}...")
        
        if errors > 0:
            print(f"\n  Errors:")
            for test, traceback in result.errors:
                print(f"    - {test}")
                print(f"      {traceback[:200]}...")
    
    # Print overall summary
    print("\n" + "=" * 80)
    print("OVERALL TEST SUMMARY")
    print("=" * 80)
    print()
    
    for pattern_name, results in results_by_pattern.items():
        status = "✅ PASS" if results['success'] else "❌ FAIL"
        print(f"{pattern_name:30} {results['passed']}/{results['total']} tests passed {status}")
    
    print()
    print(f"{'Total Tests Run:':30} {total_tests}")
    print(f"{'Total Passed:':30} {total_tests - total_failures - total_errors}")
    print(f"{'Total Failed:':30} {total_failures}")
    print(f"{'Total Errors:':30} {total_errors}")
    print()
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
