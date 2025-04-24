#!/usr/bin/env python3
"""
Main test runner script for FedEx Ship API tests.
"""

import os
import sys
import importlib
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test cases to run
TEST_CASES = [
    "SH0005_test",
    "SH0006_test",
    "SH0007_test",
    "SH0008_test",
    "SH0009_test",
    "SH0018_test",
    "SH0019_test",
    "SH0203_test",
    "SH0262_test",
    "SH0439_test",
    "SH0453_test",
    "SH0457_test",
    "SH0460_test",
    "SH0464_test",
    "SH0473_test"
]

def run_tests():
    """Run all test cases"""
    print("\n=== Running FedEx Ship API Tests ===\n")
    
    results = {}
    
    # Add the current directory to the Python path
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Run each test case
    for test_case in TEST_CASES:
        print(f"\n\n{'='*80}")
        print(f"Running test case: {test_case}")
        print(f"{'='*80}\n")
        
        try:
            # Import the test module
            module = importlib.import_module(test_case)
            
            # Get the test function (assuming it's named test_XXXX)
            test_func_name = f"test_{test_case.split('_')[0].lower()}"
            test_func = getattr(module, test_func_name)
            
            # Run the test
            result = test_func()
            results[test_case] = result
            
            # Wait a bit between tests to avoid rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"Error running test case {test_case}: {str(e)}")
            results[test_case] = False
    
    # Print summary
    print("\n\n")
    print("="*80)
    print("Test Results Summary")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for test_case, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        if result:
            passed += 1
        else:
            failed += 1
        print(f"{test_case}: {status}")
    
    print("\n")
    print(f"Total tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    return passed == len(results)

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
