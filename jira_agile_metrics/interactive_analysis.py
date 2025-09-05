"""
Interactive analysis module for JIRA Agile Metrics.

This module provides utilities for creating interactive visualizations
and analysis tools, particularly for Jupyter notebook environments.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class InteractiveScatterPlot:
    """
    Creates interactive scatter plots for cycle time analysis with clickable
    data points that link to JIRA issues.
    """
    
    def __init__(self, scatter_data: pd.DataFrame, server_url: str = None):
        """
        Initialize the interactive scatter plot.
        
        Args:
            scatter_data: DataFrame from calculate_scatterplot_data()
            server_url: JIRA server URL for constructing issue links
        """
        self.scatter_data = scatter_data.copy()
        self.server_url = server_url
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare data for plotting by adding calculated fields."""
        # Convert cycle_time to days (numeric)
        self.scatter_data['cycle_time_days'] = (
            self.scatter_data['cycle_time'].dt.total_seconds() / (24 * 3600)
        )
        
        # Create hover text with issue details
        self.scatter_data['hover_text'] = self._create_hover_text()
        
        # Ensure URL column exists
        if 'url' not in self.scatter_data.columns and self.server_url:
            self.scatter_data['url'] = (
                self.server_url.rstrip('/') + '/browse/' + self.scatter_data['key']
            )
    
    def _create_hover_text(self) -> pd.Series:
        """Create rich hover text for data points."""
        hover_text = (
            "<b>" + self.scatter_data['key'] + "</b><br>" +
            "Summary: " + self.scatter_data['summary'].str[:50] + "...<br>" +
            "Cycle Time: " + self.scatter_data['cycle_time_days'].round(1).astype(str) + " days<br>" +
            "Completed: " + self.scatter_data['completed_date'].dt.strftime('%Y-%m-%d') + "<br>" +
            "Status: " + self.scatter_data['status'] + "<br>" +
            "Type: " + self.scatter_data['issue_type'] + "<br>"
        )
        
        if 'blocked_days' in self.scatter_data.columns:
            hover_text += "Blocked Days: " + self.scatter_data['blocked_days'].astype(str) + "<br>"
        
        hover_text += "<i>Click to open in JIRA</i>"
        
        return hover_text
    
    def create_plot(self, 
                   title: str = "Interactive Cycle Time Scatter Plot",
                   color_by: str = "blocked_days",
                   size_by: Optional[str] = None,
                   percentiles: List[float] = [0.5, 0.85, 0.95],
                   height: int = 600) -> go.Figure:
        """
        Create the interactive scatter plot.
        
        Args:
            title: Plot title
            color_by: Column to use for color coding points
            size_by: Optional column to use for sizing points
            percentiles: List of percentiles to show as horizontal lines
            height: Plot height in pixels
            
        Returns:
            Plotly Figure object
        """
        if len(self.scatter_data) == 0:
            raise ValueError("No data available for plotting")
        
        fig = go.Figure()
        
        # Determine color and size settings
        color_data = self.scatter_data.get(color_by, None)
        size_data = self.scatter_data.get(size_by, 8) if size_by else 8
        
        # Create marker configuration
        marker_config = dict(
            size=size_data,
            line=dict(width=1, color='DarkSlateGrey')
        )
        
        if color_data is not None:
            marker_config.update({
                'color': color_data,
                'colorscale': 'Reds',
                'colorbar': dict(title=color_by.replace('_', ' ').title())
            })
        
        # Add scatter trace
        fig.add_trace(go.Scatter(
            x=self.scatter_data['completed_date'],
            y=self.scatter_data['cycle_time_days'],
            mode='markers',
            marker=marker_config,
            text=self.scatter_data['hover_text'],
            hovertemplate='%{text}<extra></extra>',
            customdata=self.scatter_data.get('url', ''),
            name='Issues'
        ))
        
        # Add percentile lines
        self._add_percentile_lines(fig, percentiles)
        
        # Update layout
        fig.update_layout(
            title={
                'text': f'{title}<br><sub>Click on data points to open JIRA issues</sub>',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Completion Date',
            yaxis_title='Cycle Time (Days)',
            hovermode='closest',
            height=height,
            showlegend=False
        )
        
        return fig
    
    def _add_percentile_lines(self, fig: go.Figure, percentiles: List[float]):
        """Add percentile lines to the plot."""
        colors = ['green', 'orange', 'red', 'purple', 'brown']
        
        for i, p in enumerate(percentiles):
            if i >= len(colors):
                break
                
            percentile_value = self.scatter_data['cycle_time_days'].quantile(p)
            fig.add_hline(
                y=percentile_value,
                line_dash="dash",
                line_color=colors[i],
                annotation_text=f"{int(p*100)}% ({percentile_value:.1f} days)",
                annotation_position="top left"
            )
    
    def get_summary_stats(self) -> Dict[str, float]:
        """Get summary statistics for the data."""
        if len(self.scatter_data) == 0:
            return {}
        
        stats = {
            'Total Issues': len(self.scatter_data),
            'Average Cycle Time (days)': self.scatter_data['cycle_time_days'].mean(),
            'Median Cycle Time (days)': self.scatter_data['cycle_time_days'].median(),
            'Min Cycle Time (days)': self.scatter_data['cycle_time_days'].min(),
            'Max Cycle Time (days)': self.scatter_data['cycle_time_days'].max(),
            'Std Dev Cycle Time (days)': self.scatter_data['cycle_time_days'].std(),
        }
        
        # Add percentile stats
        for p in [0.5, 0.75, 0.85, 0.95]:
            stats[f'{int(p*100)}th Percentile (days)'] = self.scatter_data['cycle_time_days'].quantile(p)
        
        # Add blocked days stats if available
        if 'blocked_days' in self.scatter_data.columns:
            stats.update({
                'Average Blocked Days': self.scatter_data['blocked_days'].mean(),
                'Median Blocked Days': self.scatter_data['blocked_days'].median(),
                'Total Blocked Days': self.scatter_data['blocked_days'].sum(),
            })
        
        return stats


class JiraConnectionHelper:
    """Helper class for managing JIRA connections in interactive environments."""
    
    @staticmethod
    def create_connection(server: str, username: str, password: str) -> 'JIRA':
        """
        Create a JIRA connection with error handling.
        
        Args:
            server: JIRA server URL
            username: Username or email
            password: Password or API token
            
        Returns:
            JIRA client instance
            
        Raises:
            Exception: If connection fails
        """
        from jira import JIRA
        
        try:
            jira_client = JIRA(
                server=server,
                basic_auth=(username, password)
            )
            
            # Test connection
            user = jira_client.current_user()
            logger.info(f"Connected to JIRA as {user}")
            
            return jira_client
            
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {e}")
            raise
    
    @staticmethod
    def validate_jql(jira_client: 'JIRA', jql: str, max_results: int = 1) -> bool:
        """
        Validate a JQL query without fetching all results.
        
        Args:
            jira_client: JIRA client instance
            jql: JQL query to validate
            max_results: Maximum results to fetch for validation
            
        Returns:
            True if query is valid, False otherwise
        """
        try:
            jira_client.search_issues(jql, maxResults=max_results)
            return True
        except Exception as e:
            logger.error(f"Invalid JQL query: {e}")
            return False


def create_workflow_template() -> List[Dict[str, Any]]:
    """
    Create a default workflow template that can be customized.
    
    Returns:
        List of workflow stage dictionaries
    """
    return [
        {"name": "Backlog", "statuses": ["Backlog", "New", "Open"]},
        {"name": "Committed", "statuses": ["To Do", "Ready", "Next"]},
        {"name": "In Progress", "statuses": ["In Progress", "Development"]},
        {"name": "Review", "statuses": ["Code Review", "Review", "Testing"]},
        {"name": "Done", "statuses": ["Done", "Closed", "Resolved"]}
    ]


def export_analysis_results(cycle_data: pd.DataFrame, 
                          scatter_data: pd.DataFrame,
                          filename_prefix: str = "jira_analysis") -> List[str]:
    """
    Export analysis results to CSV files.
    
    Args:
        cycle_data: Full cycle time data
        scatter_data: Scatter plot data
        filename_prefix: Prefix for output filenames
        
    Returns:
        List of created filenames
    """
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    created_files = []
    
    # Export cycle data
    if cycle_data is not None and len(cycle_data) > 0:
        cycle_filename = f"{filename_prefix}_cycle_data_{timestamp}.csv"
        cycle_data.to_csv(cycle_filename, index=False)
        created_files.append(cycle_filename)
    
    # Export scatter data
    if scatter_data is not None and len(scatter_data) > 0:
        scatter_filename = f"{filename_prefix}_scatter_data_{timestamp}.csv"
        scatter_data.to_csv(scatter_filename, index=False)
        created_files.append(scatter_filename)
        
        # Export summary statistics
        plotter = InteractiveScatterPlot(scatter_data)
        stats = plotter.get_summary_stats()
        
        if stats:
            summary_df = pd.DataFrame(list(stats.items()), columns=['Metric', 'Value'])
            summary_filename = f"{filename_prefix}_summary_{timestamp}.csv"
            summary_df.to_csv(summary_filename, index=False)
            created_files.append(summary_filename)
    
    return created_files