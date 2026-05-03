"""
Run tests and capture output
"""
import os
import sys
import django
import subprocess

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shelfly.settings')
django.setup()

# Import test runner
from django.test.utils import get_runner
from django.conf import settings

# Get the test runner
TestRunner = get_runner(settings)

# Create test runner instance
test_runner = TestRunner(verbosity=2, interactive=False, keepdb=True)

print("=" * 70)
print("RUNNING STRATEGY PATTERN TESTS")
print("=" * 70)

# Run strategy pattern tests
failures = test_runner.run_tests(["bookstore.tests.test_strategy_pattern"])

print("\n" + "=" * 70)
print(f"STRATEGY PATTERN TESTS: {'PASSED' if failures == 0 else 'FAILED'}")
print(f"Failures: {failures}")
print("=" * 70)

sys.exit(failures)
