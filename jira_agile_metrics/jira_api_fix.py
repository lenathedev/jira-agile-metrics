"""
JIRA API v3 endpoint fix for the new /rest/api/3/search/jql endpoint.

This module provides a workaround for the JIRA library to use the new
search/jql endpoint instead of the deprecated search endpoint.
"""

import logging
from typing import Any, Dict, List, Union
from jira import JIRA
from jira.resources import Issue

logger = logging.getLogger(__name__)


def patch_jira_search_issues():
    """
    Monkey-patch the JIRA library to use the new search/jql endpoint.
    
    This fixes the HTTP 410 error when using the deprecated /rest/api/3/search endpoint.
    """
    
    def new_search_issues(
        self,
        jql_str: str,
        startAt: int = 0,
        maxResults: int = 50,
        validate_query: bool = True,
        fields: Union[str, List[str], None] = '*all',
        expand: str = None,
        properties: str = None,
        *,
        json_result: bool = False,
        use_post: bool = False
    ):
        """
        Search for issues using JQL with the new API v3 search/jql endpoint.
        
        This is a patched version that uses /rest/api/3/search/jql instead of
        the deprecated /rest/api/3/search endpoint.
        """
        
        # Build the request parameters
        params = {
            'jql': jql_str,
            'startAt': startAt,
            'maxResults': maxResults,
            'validateQuery': validate_query,
        }
        
        if fields:
            if isinstance(fields, str):
                params['fields'] = fields
            else:
                params['fields'] = ','.join(fields)
        
        if expand:
            params['expand'] = expand
            
        if properties:
            params['properties'] = properties
        
        # Use the new search/jql endpoint
        # Build the URL manually since _get_url might not work for the new endpoint
        base_url = self._options['server'].rstrip('/')
        api_path = f"/rest/{self._options['rest_path']}/{self._options['rest_api_version']}"
        url = f"{base_url}{api_path}/search/jql"
        
        logger.debug(f"Searching issues with new endpoint: {url}")
        logger.debug(f"JQL: {jql_str}")
        logger.debug(f"Parameters: {params}")
        
        try:
            if use_post:
                # For POST requests, send data in body
                response = self._session.post(url, json=params)
            else:
                # For GET requests, send as query parameters
                response = self._session.get(url, params=params)
            
            response.raise_for_status()
            result = response.json()
            
            if json_result:
                return result
            
            # Convert to Issue objects like the original method
            issues = []
            for issue_data in result.get('issues', []):
                issue = Issue(self._options, self._session, issue_data)
                issues.append(issue)
            
            # Create a result list with pagination info
            from jira.client import ResultList
            result_list = ResultList(
                issues,
                startAt=result.get('startAt', 0),
                maxResults=result.get('maxResults', maxResults),
                total=result.get('total', len(issues)),
                isLast=result.get('isLast', True)
            )
            
            return result_list
            
        except Exception as e:
            logger.error(f"Search failed with new endpoint: {e}")
            # If the new endpoint fails, try to fall back to the original method
            logger.warning("Falling back to original search method")
            return self._original_search_issues(
                jql_str, startAt, maxResults, validate_query, 
                fields, expand, properties, 
                json_result=json_result, use_post=use_post
            )
    
    # Store the original method before patching
    if not hasattr(JIRA, '_original_search_issues'):
        JIRA._original_search_issues = JIRA.search_issues
    
    # Apply the patch
    JIRA.search_issues = new_search_issues
    logger.info("Applied JIRA search_issues patch for new API v3 search/jql endpoint")


def unpatch_jira_search_issues():
    """
    Remove the monkey-patch and restore the original search_issues method.
    """
    if hasattr(JIRA, '_original_search_issues'):
        JIRA.search_issues = JIRA._original_search_issues
        delattr(JIRA, '_original_search_issues')
        logger.info("Removed JIRA search_issues patch")


class PatchedJIRA(JIRA):
    """
    A JIRA client class that automatically applies the search/jql endpoint patch.
    
    Use this instead of the regular JIRA class to automatically get the fix.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply the patch to this instance
        patch_jira_search_issues()
        logger.info("Created PatchedJIRA client with search/jql endpoint fix")


def create_patched_jira_client(options: Dict[str, Any], basic_auth: tuple) -> JIRA:
    """
    Create a JIRA client with the search/jql endpoint patch applied.
    
    Args:
        options: JIRA client options dictionary
        basic_auth: Tuple of (username, password/token)
        
    Returns:
        JIRA client instance with the patch applied
    """
    
    # Ensure we're using API v3
    if 'rest_api_version' not in options:
        options['rest_api_version'] = '3'
    
    # Apply the global patch
    patch_jira_search_issues()
    
    # Create the client
    client = JIRA(options=options, basic_auth=basic_auth)
    
    logger.info("Created JIRA client with search/jql endpoint patch")
    return client