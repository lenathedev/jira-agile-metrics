# Interactive Cycle Time Analysis

This extension adds interactive Jupyter notebook capabilities to the JIRA Agile Metrics project, allowing you to create clickable scatter plots with direct links to JIRA issues.

## Features

- **Interactive Jupyter Notebook**: Easy-to-use interface for JIRA analysis
- **Clickable Scatter Plots**: Data points link directly to JIRA issues
- **Rich Tooltips**: Hover for detailed issue information
- **Color Coding**: Points colored by blocked days or other metrics
- **Percentile Lines**: Visual indicators for 50th, 85th, and 95th percentiles
- **Data Export**: Export results to CSV for further analysis
- **Configurable Workflows**: Adapt to your team's JIRA workflow

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Launch Jupyter Notebook

```bash
jupyter notebook interactive_cycle_time_analysis.ipynb
```

### 3. Follow the Notebook Steps

1. **Connect to JIRA**: Enter your credentials
2. **Configure Workflow**: Map JIRA statuses to workflow stages
3. **Enter JQL Query**: Specify which issues to analyze
4. **Run Analysis**: Fetch and process data
5. **Generate Plot**: Create interactive visualization
6. **Export Data**: Save results for further use

## Alternative: Command Line Script

For a simpler command-line interface:

```bash
python examples/interactive_analysis_example.py
```

## Configuration

### JIRA Connection

- **Server URL**: Your JIRA instance URL (e.g., `https://company.atlassian.net`)
- **Username**: Your email or username
- **API Token**: Generate from JIRA Account Settings → Security → API tokens

### Workflow Configuration

Default workflow stages:

```python
[
    {"name": "Backlog", "statuses": ["Backlog", "New", "Open"]},
    {"name": "Committed", "statuses": ["To Do", "Ready", "Next"]},
    {"name": "In Progress", "statuses": ["In Progress", "Development"]},
    {"name": "Review", "statuses": ["Code Review", "Review", "Testing"]},
    {"name": "Done", "statuses": ["Done", "Closed", "Resolved"]}
]
```

Customize this to match your team's workflow.

### JQL Query Examples

```sql
-- Stories completed in last 90 days
project = "MYPROJ" AND issuetype = Story AND resolved >= -90d

-- All issues for a specific team
project = "MYPROJ" AND "Team" = "Platform Team" AND status = Done

-- Issues with specific labels
project = "MYPROJ" AND labels in (performance, security) AND resolved >= -30d
```

## Interactive Features

### Scatter Plot Interactions

- **Hover**: View issue details in tooltip
- **Click**: Open JIRA issue in new browser tab
- **Zoom**: Use mouse wheel or plot controls
- **Pan**: Click and drag to move around

### Color Coding Options

- **Blocked Days**: Red intensity shows time spent blocked
- **Issue Type**: Different colors for Story, Bug, Task, etc.
- **Team**: Color by team assignment
- **Custom Fields**: Any numeric JIRA field

### Percentile Lines

- **Green (50%)**: Median cycle time
- **Orange (85%)**: Good performance target
- **Red (95%)**: Issues taking longer than 95% of others

## Data Export

The notebook exports three CSV files:

1. **Full Cycle Data**: Complete dataset with all workflow stages
2. **Scatter Plot Data**: Filtered data used for visualization
3. **Summary Statistics**: Key metrics and percentiles

## Programmatic Usage

Use the interactive analysis module in your own scripts:

```python
from jira_agile_metrics.interactive_analysis import InteractiveScatterPlot
from jira_agile_metrics.calculators.scatterplot import calculate_scatterplot_data

# Create scatter plot
plotter = InteractiveScatterPlot(scatter_data, server_url)
fig = plotter.create_plot(
    title="My Team's Cycle Time",
    color_by="blocked_days",
    percentiles=[0.5, 0.85, 0.95]
)

# Show in browser
fig.show()

# Get statistics
stats = plotter.get_summary_stats()
print(f"Average cycle time: {stats['Average Cycle Time (days)']:.1f} days")
```

## Troubleshooting

### Common Issues

**"No module named 'plotly'"**
```bash
pip install plotly ipywidgets
```

**"Connection failed"**
- Verify JIRA URL (include https://)
- Use API token instead of password
- Check network connectivity

**"No issues with cycle times found"**
- Verify workflow configuration matches your JIRA statuses
- Check JQL query returns completed issues
- Ensure issues have moved through workflow stages

**"Invalid JQL query"**
- Test query in JIRA's issue search
- Check field names and project keys
- Verify permissions to access projects

### Performance Tips

- Start with small datasets (limit to 100-500 issues)
- Use specific date ranges in JQL queries
- Filter by project or team to reduce data volume
- Export data for offline analysis of large datasets

## Security Notes

- Use API tokens instead of passwords
- Don't commit credentials to version control
- Consider using environment variables for sensitive data
- API tokens can be revoked if compromised

## Dependencies

The interactive features require additional packages:

- `plotly>=5.0.0` - Interactive plotting
- `ipywidgets>=8.0.0` - Jupyter notebook widgets
- `jupyter` - Notebook environment

These are automatically installed with the updated requirements.txt.

## Examples

See the `examples/` directory for:

- `interactive_analysis_example.py` - Command-line script
- Sample configuration files
- Advanced usage patterns

## Contributing

To add new interactive features:

1. Extend the `InteractiveScatterPlot` class
2. Add new visualization types to the notebook
3. Update this documentation
4. Add tests for new functionality

## Support

For issues specific to the interactive features:

1. Check this documentation
2. Review the example scripts
3. Test with a small dataset first
4. Open an issue with error details and configuration