#!/usr/bin/env python3
"""
Example script demonstrating interactive cycle time analysis.

This script shows how to use the interactive analysis module
to create clickable scatter plots with JIRA issue links.
"""

import sys
import os
import getpass
from datetime import datetime

# Add the parent directory to the path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jira_agile_metrics.interactive_analysis import (
    InteractiveScatterPlot, 
    JiraConnectionHelper,
    create_workflow_template,
    export_analysis_results
)
from jira_agile_metrics.querymanager import QueryManager
from jira_agile_metrics.calculators.cycletime import calculate_cycle_times
from jira_agile_metrics.calculators.scatterplot import calculate_scatterplot_data


def main():
    """Main function demonstrating interactive analysis workflow."""
    
    print("🚀 JIRA Interactive Cycle Time Analysis")
    print("=" * 50)
    
    # Step 1: Get JIRA connection details
    print("\n1. JIRA Connection Setup")
    print("-" * 30)
    
    server = input("JIRA Server URL: ").strip()
    if not server:
        server = "https://your-company.atlassian.net"
    
    username = input("Username/Email: ").strip()
    if not username:
        print("❌ Username is required")
        return
    
    password = getpass.getpass("API Token/Password: ")
    if not password:
        print("❌ Password/token is required")
        return
    
    # Step 2: Connect to JIRA
    print("\n2. Connecting to JIRA...")
    print("-" * 30)
    
    try:
        jira_client = JiraConnectionHelper.create_connection(server, username, password)
        print(f"✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Step 3: Configure workflow
    print("\n3. Workflow Configuration")
    print("-" * 30)
    
    workflow = create_workflow_template()
    print("Using default workflow:")
    for stage in workflow:
        print(f"  - {stage['name']}: {', '.join(stage['statuses'])}")
    
    committed_column = "Committed"
    done_column = "Done"
    
    # Step 4: Get JQL query
    print("\n4. JQL Query")
    print("-" * 30)
    
    default_jql = "project = 'YOUR_PROJECT' AND issuetype = Story AND status in (Done, Closed) ORDER BY resolved DESC"
    jql = input(f"JQL Query [{default_jql}]: ").strip()
    if not jql:
        jql = default_jql
    
    max_results = input("Max Results [100]: ").strip()
    max_results = int(max_results) if max_results.isdigit() else 100
    
    # Step 5: Validate JQL
    print(f"\n5. Validating JQL query...")
    print("-" * 30)
    
    if not JiraConnectionHelper.validate_jql(jira_client, jql):
        print("❌ Invalid JQL query. Please check your query and try again.")
        return
    
    print("✅ JQL query is valid")
    
    # Step 6: Fetch and analyze data
    print(f"\n6. Fetching and analyzing data...")
    print("-" * 30)
    
    try:
        # Create settings
        settings = {
            'max_results': max_results,
            'attributes': {},
            'known_values': {}
        }
        
        # Create query manager
        query_manager = QueryManager(jira_client, settings)
        
        # Calculate cycle times
        print("📊 Calculating cycle times...")
        cycle_data = calculate_cycle_times(
            query_manager,
            workflow,
            {},  # attributes
            committed_column,
            done_column,
            [{'jql': jql, 'value': 'Analysis'}],
            None  # query_attribute
        )
        
        print(f"✅ Found {len(cycle_data)} issues")
        
        # Calculate scatter plot data
        scatter_data = calculate_scatterplot_data(cycle_data)
        print(f"✅ {len(scatter_data)} issues have cycle times")
        
        if len(scatter_data) == 0:
            print("❌ No issues with cycle times found. Check your workflow configuration.")
            return
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return
    
    # Step 7: Create interactive plot
    print(f"\n7. Creating interactive visualization...")
    print("-" * 30)
    
    try:
        # Create the interactive scatter plot
        plotter = InteractiveScatterPlot(scatter_data, server)
        fig = plotter.create_plot(
            title="JIRA Cycle Time Analysis",
            color_by="blocked_days",
            percentiles=[0.5, 0.85, 0.95]
        )
        
        # Show the plot (this will open in browser)
        fig.show()
        
        # Display summary statistics
        stats = plotter.get_summary_stats()
        print("\n📈 Summary Statistics:")
        for metric, value in stats.items():
            if isinstance(value, float):
                print(f"  {metric}: {value:.1f}")
            else:
                print(f"  {metric}: {value}")
        
    except Exception as e:
        print(f"❌ Visualization failed: {e}")
        return
    
    # Step 8: Export data
    print(f"\n8. Exporting data...")
    print("-" * 30)
    
    export_choice = input("Export data to CSV files? [y/N]: ").strip().lower()
    if export_choice in ['y', 'yes']:
        try:
            created_files = export_analysis_results(
                cycle_data, 
                scatter_data, 
                f"jira_analysis_{datetime.now().strftime('%Y%m%d')}"
            )
            
            print("✅ Data exported to:")
            for filename in created_files:
                print(f"  - {filename}")
                
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    print(f"\n🎉 Analysis complete!")
    print("The interactive plot should have opened in your browser.")
    print("Click on data points to open JIRA issues in new tabs.")


if __name__ == "__main__":
    main()