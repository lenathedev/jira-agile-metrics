"""
Fixed QueryManager that uses the new JIRA search/jql endpoint directly.

This module provides a drop-in replacement for QueryManager that bypasses
the JIRA library's search_issues method and uses direct API calls.
"""

import logging
import requests
from typing import List, Dict, Any
from jira.resources import Issue
from .querymanager import QueryManager

logger = logging.getLogger(__name__)


class FixedQueryManager(QueryManager):
    """
    QueryManager that uses direct API calls to the new search/jql endpoint.
    
    This bypasses the JIRA library's search_issues method which uses the
    deprecated /rest/api/3/search endpoint.
    """
    
    def find_issues(self, jql: str, expand: str = "changelog") -> List[Issue]:
        """
        Find issues using the new search/jql endpoint directly.
        
        Args:
            jql: JQL query string
            expand: Fields to expand (default: "changelog")
            
        Returns:
            List of Issue objects
        """
        max_results = self.settings.get("max_results")
        
        logger.info("Fetching issues with query `%s` using fixed endpoint", jql)
        if max_results:
            logger.info("Limiting to %d results", max_results)
        
        # Build the request parameters
        params = {
            'jql': jql,
            'startAt': 0,
            'maxResults': max_results or 1000,  # Default to 1000 if not specified
            'validateQuery': True,
            'fields': '*all',
            'expand': expand
        }
        
        # Build the URL for the new endpoint
        base_url = self.jira._options['server'].rstrip('/')
        api_path = f"/rest/{self.jira._options['rest_path']}/{self.jira._options['rest_api_version']}"
        url = f"{base_url}{api_path}/search/jql"
        
        logger.debug(f"Using new search/jql endpoint: {url}")
        logger.debug(f"Parameters: {params}")
        
        try:
            # Make the request using the JIRA client's session (for auth)
            response = self.jira._session.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            
            # Convert to Issue objects
            issues = []
            for issue_data in result.get('issues', []):
                issue = Issue(self.jira._options, self.jira._session, issue_data)
                issues.append(issue)
            
            logger.info("Fetched %d issues using new endpoint", len(issues))
            return issues
            
        except Exception as e:
            logger.error(f"Failed to fetch issues with new endpoint: {e}")
            logger.warning("Falling back to original search method")
            
            # Fallback to the original method
            try:
                issues = self.jira.search_issues(
                    jql, expand=expand, maxResults=max_results or 1000
                )
                logger.info("Fetched %d issues using fallback method", len(issues))
                return issues
            except Exception as fallback_error:
                logger.error(f"Fallback method also failed: {fallback_error}")
                raise e


def create_fixed_query_manager(jira_client, settings: Dict[str, Any]) -> FixedQueryManager:
    """
    Create a FixedQueryManager that uses the new search/jql endpoint.
    
    Args:
        jira_client: JIRA client instance
        settings: Settings dictionary
        
    Returns:
        FixedQueryManager instance
    """
    return FixedQueryManager(jira_client, settings)