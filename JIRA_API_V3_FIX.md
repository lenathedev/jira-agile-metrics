# JIRA API v3 Fix

## Problem
You may encounter this error when running the interactive analysis:

```
JiraError HTTP 410: The requested API has been removed. 
Please migrate to the /rest/api/3/search/jql API.
```

## Solution
This has been **automatically fixed** in the interactive analysis module. The system now uses JIRA REST API v3 by default.

## What Was Changed

### 1. Interactive Analysis Module
- Updated `JiraConnectionHelper.create_connection()` to use API v3
- Updated `JiraConnectionHelper.create_connection_from_config()` to use API v3
- All JIRA client connections now include `'rest_api_version': '3'`

### 2. Jupyter Notebook
- Updated JIRA client creation to use API v3
- Maintains compatibility with existing configuration files

### 3. Configuration Templates
- Updated examples to document API v3 usage
- Added optional client configuration examples

## Technical Details

### Before (API v2 - deprecated)
```python
jira_client = JIRA(
    server=server_url,
    basic_auth=(username, token)
)
```

### After (API v3 - current)
```python
options = {
    'server': server_url,
    'rest_api_version': '3'
}

jira_client = JIRA(
    options=options,
    basic_auth=(username, token)
)
```

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