#!/usr/bin/env python3
"""
Simple test runner to validate current system
Run this before making any changes to establish baseline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def quick_test():
    """Run a few quick tests to validate system"""
    from test_runner import CreditCardTestRunner
    
    print("🚀 Quick validation test...")
    
    # Simple test cases to validate core functionality
    quick_tests = [
        {
            "category": "Basic Milestone Test",
            "query": "If I spend ₹7.5 lakh yearly on Atlas, how many miles do I get?",
            "expected_keywords": ["15,000", "2,500", "milestone"],
            "critical": True
        },
        {
            "category": "Basic Hotel Cap Test", 
            "query": "If I spend ₹3 lakh on hotels which card wins?",
            "expected_keywords": ["10,000", "2,000", "Atlas"],
            "critical": True
        },
        {
            "category": "Basic Utility Test",
            "query": "Do I get points on utility spends using ICICI EPM?",
            "expected_keywords": ["6 points", "1,000", "cap"],
            "critical": False
        }
    ]
    
    try:
        runner = CreditCardTestRunner()
        print("✅ System initialized successfully")
        
        results = []
        for i, test in enumerate(quick_tests, 1):
            print(f"\n[{i}/{len(quick_tests)}] Testing: {test['query'][:50]}...")
            result = runner.run_test(test)
            results.append(result)
            
            status_emoji = {"PASSING": "✅", "PARTIAL": "⚠️", "FAILING": "❌", "ERROR": "💥"}
            print(f"   {status_emoji.get(result['status'], '❓')} {result['status']} (Score: {result['score']:.2f})")
            
            if result['missing_keywords']:
                print(f"   Missing: {', '.join(result['missing_keywords'])}")
        
        # Summary
        passing = len([r for r in results if r['status'] == 'PASSING'])
        critical_failing = len([r for r in results if r.get('critical') and r['status'] in ['FAILING', 'ERROR']])
        
        print(f"\n📊 Quick Test Summary: {passing}/{len(results)} passing")
        
        if critical_failing > 0:
            print(f"🚨 {critical_failing} critical test(s) failed!")
            return False
        else:
            print("✅ Core functionality validated!")
            return True
            
    except Exception as e:
        print(f"❌ System validation failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_test()
    if not success:
        print("\n⚠️  System validation failed. Fix issues before making changes.")
        sys.exit(1)
    else:
        print("\n🎉 System ready for development!")
        print("📝 Run 'python tests/test_runner.py' for full test suite")