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

### 2. Create Configuration File

Copy and customize the template:

```bash
cp examples/interactive_config_template.yml my_config.yml
```

Edit `my_config.yml` with your JIRA details:

```yaml
connection:
  domain: https://your-company.atlassian.net
  username: your-email@company.com
  token: your-api-token

query: project = "YOUR_PROJECT" AND status = Done

workflow:
  Backlog: [Backlog, To Do]
  In Progress: [In Progress, Development]
  Done: [Done, Closed]
```

### 3. Launch Jupyter Notebook

```bash
jupyter notebook interactive_cycle_time_analysis.ipynb
```

### 4. Follow the Notebook Steps

1. **Load Configuration**: Enter path to your config file
2. **Review Settings**: Optionally override workflow or query settings
3. **Run Analysis**: Fetch and process data using config
4. **Generate Plot**: Create interactive visualization
5. **Export Data**: Save results for further use

## Alternative: Command Line Script

For a simpler command-line interface (still requires interactive input):

```bash
python examples/interactive_analysis_example.py
```

Or use the new config-based approach programmatically:

```python
from jira_agile_metrics.interactive_analysis import run_analysis_from_config

# Run analysis from config file
cycle_data, scatter_data, config = run_analysis_from_config(
    'my_config.yml',
    max_results=100
)

# Create interactive plot
from jira_agile_metrics.interactive_analysis import InteractiveScatterPlot
plotter = InteractiveScatterPlot(scatter_data, config['connection']['domain'])
fig = plotter.create_plot()
fig.show()
```

## Configuration

The interactive analysis now uses YAML configuration files with the same format as the main jira-agile-metrics application.

### Configuration File Structure

```yaml
# JIRA Connection
connection:
  domain: https://your-company.atlassian.net
  type: jira
  username: your-email@company.com
  token: your-api-token-here

# Query Configuration
query: project = "MYPROJECT" AND status = Done

# Workflow Configuration
workflow:
  Backlog:
    - Backlog
    - New
    - To Do
  In Progress:
    - In Progress
    - Development
  Done:
    - Done
    - Closed

# Optional: Custom field mappings
attributes:
  Team: Team
  Story Points: Story Points

# Optional: Output settings
output:
  max results: 500
  quantiles: [0.5, 0.85, 0.95]
```

### JIRA Authentication

- **API Token**: Generate from [JIRA Account Settings → Security → API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
- **Username**: Your email address
- **Domain**: Your JIRA instance URL

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

### Config-Based Analysis

```python
from jira_agile_metrics.interactive_analysis import run_analysis_from_config, InteractiveScatterPlot

# Run complete analysis from config file
cycle_data, scatter_data, config = run_analysis_from_config(
    'my_config.yml',
    max_results=100,  # Optional override
    jql_override='project = "MYPROJ" AND resolved >= -30d'  # Optional override
)

# Create interactive plot
plotter = InteractiveScatterPlot(scatter_data, config['connection']['domain'])
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

### Manual Analysis

```python
from jira_agile_metrics.interactive_analysis import InteractiveScatterPlot, load_config_file, JiraConnectionHelper
from jira_agile_metrics.querymanager import QueryManager
from jira_agile_metrics.calculators.cycletime import calculate_cycle_times

# Load config and connect
config = load_config_file('my_config.yml')
jira_client = JiraConnectionHelper.create_connection_from_config(config)
query_manager = QueryManager(jira_client, config['settings'])

# Run analysis manually
cycle_data = calculate_cycle_times(...)
scatter_data = calculate_scatterplot_data(cycle_data)

# Create plot
plotter = InteractiveScatterPlot(scatter_data)
fig = plotter.create_plot()
fig.show()
```

## Troubleshooting

### Common Issues

**"No module named 'plotly'"**
```bash
pip install plotly ipywidgets
```

**"Configuration file not found"**
- Check the file path is correct
- Use relative paths from notebook directory
- Copy from examples/ directory and customize

**"Connection failed"**
- Verify JIRA URL in config file (include https://)
- Use API token instead of password
- Check network connectivity
- Verify credentials in config file

**"No issues with cycle times found"**
- Verify workflow configuration in YAML matches your JIRA statuses
- Check JQL query in config returns completed issues
- Ensure issues have moved through workflow stages

**"Invalid JQL query"**
- Test query in JIRA's issue search first
- Check field names and project keys in config
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