#!/usr/bin/env python3
"""
Example script demonstrating config-based interactive cycle time analysis.

This script shows how to use configuration files for interactive analysis,
similar to the main jira-agile-metrics application.
"""

import sys
import os
import argparse
from datetime import datetime

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jira_agile_metrics.interactive_analysis import (
    run_analysis_from_config,
    InteractiveScatterPlot, 
    export_analysis_results
)


def main():
    """Main function demonstrating config-based interactive analysis workflow."""
    
    parser = argparse.ArgumentParser(
        description="Interactive JIRA Cycle Time Analysis using configuration files"
    )
    parser.add_argument(
        "config_file", 
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--max-results", 
        type=int, 
        help="Maximum number of issues to fetch (overrides config)"
    )
    parser.add_argument(
        "--jql-override", 
        help="JQL query to override config file"
    )
    parser.add_argument(
        "--export", 
        action="store_true", 
        help="Export results to CSV files"
    )
    parser.add_argument(
        "--no-plot", 
        action="store_true", 
        help="Skip interactive plot generation"
    )
    
    args = parser.parse_args()
    
    print("🚀 JIRA Interactive Cycle Time Analysis (Config-Based)")
    print("=" * 60)
    
    # Check if config file exists
    if not os.path.exists(args.config_file):
        print(f"❌ Configuration file not found: {args.config_file}")
        print("\nAvailable example configs:")
        examples_dir = os.path.join(os.path.dirname(__file__))
        for file in os.listdir(examples_dir):
            if file.endswith('.yml'):
                print(f"  - {os.path.join(examples_dir, file)}")
        return 1
    
    try:
        print(f"\n📁 Loading configuration from: {args.config_file}")
        print("-" * 50)
        
        # Run analysis from config
        cycle_data, scatter_data, config_options = run_analysis_from_config(
            args.config_file,
            max_results=args.max_results,
            jql_override=args.jql_override
        )
        
        print(f"✅ Analysis complete!")
        print(f"  • Total issues: {len(cycle_data)}")
        print(f"  • Issues with cycle times: {len(scatter_data)}")
        
        if len(scatter_data) == 0:
            print("❌ No issues with cycle times found.")
            print("Check your workflow configuration and ensure issues have moved through stages.")
            return 1
        
        # Display summary statistics
        plotter = InteractiveScatterPlot(scatter_data, config_options['connection']['domain'])
        stats = plotter.get_summary_stats()
        
        print(f"\n📈 Summary Statistics:")
        print("-" * 30)
        for metric, value in stats.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.1f}")
            else:
                print(f"  {metric}: {value}")
        
        # Create interactive plot
        if not args.no_plot:
            print(f"\n📊 Creating interactive visualization...")
            print("-" * 50)
            
            try:
                fig = plotter.create_plot(
                    title="JIRA Cycle Time Analysis",
                    color_by="blocked_days",
                    percentiles=[0.5, 0.85, 0.95]
                )
                
                # Show the plot (this will open in browser)
                fig.show()
                print("✅ Interactive plot opened in browser")
                print("   Click on data points to open JIRA issues!")
                
            except Exception as e:
                print(f"⚠️  Plot generation failed: {e}")
                print("   Continuing with data export...")
        
        # Export data
        if args.export:
            print(f"\n💾 Exporting data...")
            print("-" * 30)
            
            try:
                config_name = os.path.splitext(os.path.basename(args.config_file))[0]
                created_files = export_analysis_results(
                    cycle_data, 
                    scatter_data, 
                    f"jira_analysis_{config_name}_{datetime.now().strftime('%Y%m%d')}"
                )
                
                print("✅ Data exported to:")
                for filename in created_files:
                    print(f"  - {filename}")
                    
            except Exception as e:
                print(f"❌ Export failed: {e}")
        
        print(f"\n🎉 Analysis complete!")
        if not args.no_plot:
            print("The interactive plot should be open in your browser.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)