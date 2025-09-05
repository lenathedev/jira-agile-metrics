#!/usr/bin/env python3
"""
Test script to verify the JIRA endpoint fix works.

Run this script to test if the new search/jql endpoint fix resolves
the HTTP 410 error.
"""

import sys
import os
import argparse

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jira_agile_metrics.interactive_analysis import run_analysis_from_config


def test_endpoint_fix(config_file: str, max_results: int = 5):
    """
    Test the endpoint fix with a real JIRA connection.
    
    Args:
        config_file: Path to YAML configuration file
        max_results: Number of results to fetch (keep small for testing)
    """
    
    print("🧪 Testing JIRA Endpoint Fix")
    print("=" * 50)
    
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        print(f"1. Loading configuration from: {config_file}")
        print(f"2. Testing with max_results = {max_results}")
        print()
        
        # Run analysis with the fixed endpoint
        cycle_data, scatter_data, config_options = run_analysis_from_config(
            config_file,
            max_results=max_results
        )
        
        print(f"✅ SUCCESS! Analysis completed without HTTP 410 error")
        print(f"   • Total issues fetched: {len(cycle_data)}")
        print(f"   • Issues with cycle times: {len(scatter_data)}")
        print(f"   • JIRA server: {config_options['connection']['domain']}")
        print()
        
        if len(scatter_data) > 0:
            # Show a sample of the data
            sample_issue = scatter_data.iloc[0]
            print(f"📋 Sample issue:")
            print(f"   • Key: {sample_issue['key']}")
            print(f"   • Summary: {sample_issue['summary'][:50]}...")
            print(f"   • Cycle time: {sample_issue['cycle_time']}")
        
        print()
        print("🎉 The endpoint fix is working correctly!")
        print("You can now run the full analysis without issues.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
        # Check if it's still the HTTP 410 error
        if "HTTP 410" in str(e):
            print()
            print("🔍 Still getting HTTP 410 error. This could mean:")
            print("   1. The fix wasn't applied correctly")
            print("   2. Your local environment has a different JIRA library version")
            print("   3. There might be a caching issue")
            print()
            print("💡 Try restarting your Jupyter kernel and running again.")
        
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        
        return False


def main():
    parser = argparse.ArgumentParser(description="Test JIRA endpoint fix")
    parser.add_argument("config_file", help="Path to YAML configuration file")
    parser.add_argument("--max-results", type=int, default=5, 
                       help="Maximum number of issues to fetch for testing")
    
    args = parser.parse_args()
    
    success = test_endpoint_fix(args.config_file, args.max_results)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()