# JIRA API v3 Fix

## Problem
You may encounter this error when running the interactive analysis:

```
JiraError HTTP 410: The requested API has been removed. 
Please migrate to the /rest/api/3/search/jql API.
```

This occurs because Atlassian has deprecated the `/rest/api/3/search` endpoint and now requires the `/rest/api/3/search/jql` endpoint.

## Solution
This has been **automatically fixed** with a patched JIRA client that uses the new `/rest/api/3/search/jql` endpoint. The system now includes a monkey-patch that redirects search requests to the correct endpoint.

## What Was Changed

### 1. New JIRA API Fix Module
- Created `jira_agile_metrics/jira_api_fix.py` with endpoint patch
- Implements `create_patched_jira_client()` function
- Monkey-patches the JIRA library to use `/rest/api/3/search/jql`
- Includes fallback to original method if new endpoint fails

### 2. Interactive Analysis Module
- Updated to use `create_patched_jira_client()` instead of direct JIRA client
- Automatically applies the search/jql endpoint fix
- Maintains all existing functionality

### 3. Jupyter Notebook
- Updated to import and use the patched JIRA client
- Automatically handles the new endpoint requirement
- No changes needed to existing configuration files

### 4. Configuration Templates
- Updated examples to document the automatic fix
- Added troubleshooting information for the new endpoint

## Technical Details

### Before (Deprecated endpoint)
```python
# This would fail with HTTP 410
jira_client = JIRA(options={'server': url, 'rest_api_version': '3'}, basic_auth=auth)
result = jira_client.search_issues(jql)  # Uses /rest/api/3/search (deprecated)
```

### After (Fixed endpoint)
```python
# This works with the new endpoint
from jira_agile_metrics.jira_api_fix import create_patched_jira_client

jira_client = create_patched_jira_client(
    options={'server': url, 'rest_api_version': '3'},
    basic_auth=auth
)
result = jira_client.search_issues(jql)  # Uses /rest/api/3/search/jql (current)
```

### How the Patch Works
The patch intercepts calls to `search_issues()` and:
1. Builds the correct URL: `/rest/api/3/search/jql`
2. Sends the request to the new endpoint
3. Processes the response in the same format as the original method
4. Falls back to the original method if the new endpoint fails

## Configuration Options

You can customize JIRA client behavior in your config file:

```yaml
connection:
  domain: https://your-company.atlassian.net
  username: your-email@company.com
  token: your-api-token
  
  # Optional: JIRA client options
  jira client options:
    timeout: 30        # Request timeout in seconds
    verify: true       # SSL verification (default: true)
    # rest_api_version: '3'  # Automatically set
```

## Compatibility

- **JIRA Cloud**: ✅ Fully supported with API v3
- **JIRA Server 8.0+**: ✅ Supports API v3
- **JIRA Server 7.x**: ⚠️ May need API v2 (contact admin)
- **JIRA Server 6.x**: ❌ Not supported

## If You Still Have Issues

1. **Check JIRA Version**: Ensure your JIRA instance supports API v3
2. **Test Connection**: Try the connection in a browser: `https://your-jira.com/rest/api/3/myself`
3. **Check Permissions**: Ensure your API token has sufficient permissions
4. **Contact Admin**: For JIRA Server instances, check with your administrator

## Manual Override (if needed)

If you need to use API v2 for older JIRA instances:

```yaml
connection:
  domain: https://your-jira-server.com
  username: your-username
  token: your-token
  
  jira client options:
    rest_api_version: '2'  # Override to use v2
```

**Note**: API v2 is deprecated and may stop working in newer JIRA Cloud instances.