# Get Users Tool Documentation

## 📋 Overview

The `get_users` tool is a simple, efficient MCP database tool designed for retrieving user information with minimal complexity. It provides clean access to user data with built-in pagination and filtering capabilities.

## 🎯 Purpose

Unlike the more complex `search_users` tool, `get_users` is designed for:
- Simple user listing operations
- Retrieving specific users by ID
- Paginated user browsing
- Basic active/inactive user filtering

## 🔧 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `user_id` | Optional[str] | None | Retrieve a specific user by ID |
| `limit` | Optional[int] | 50 | Maximum users to return (1-1000) |
| `offset` | Optional[int] | 0 | Records to skip (for pagination) |
| `active_only` | Optional[bool] | True | Filter by user status |

## 📝 Usage Examples

### Basic Usage

```python
# Get first 50 active users (default behavior)
get_users()

# Get a specific user
get_users(user_id="123")

# Get first 10 users
get_users(limit=10)
```

### Advanced Usage

```python
# Get all users (active and inactive)
get_users(active_only=False, limit=100)

# Pagination - second page of 20 users
get_users(limit=20, offset=20)

# Get inactive users only
get_users(active_only=False, limit=50)
```

## 📊 Response Format

### Success Response
```json
{
  "success": true,
  "message": "Successfully retrieved 5 user(s)",
  "total_returned": 5,
  "query_params": {
    "user_id": null,
    "limit": 50,
    "offset": 0,
    "active_only": true
  },
  "users": [
    {
      "id": "1",
      "first_name": "Jean",
      "last_name": "Dupont",
      "email": "jean.dupont@company.com",
      "phone": "+33123456789",
      "role": "worker",
      "specialization": "electrician",
      "is_active": true,
      "created_at": "2025-01-01T10:00:00",
      "updated_at": "2025-01-15T14:30:00"
    }
  ]
}
```

### Error Response
```json
{
  "success": false,
  "error": "Parameter validation failed",
  "message": "Limit must be between 1 and 1000",
  "query_params": {
    "user_id": null,
    "limit": 2000,
    "offset": 0,
    "active_only": true
  }
}
```

## 🔍 User Fields Returned

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique user identifier |
| `first_name` | string | User's first name |
| `last_name` | string | User's last name |
| `email` | string | Email address |
| `phone` | string | Phone number |
| `role` | string | User role (worker, chief, manager, admin) |
| `specialization` | string | Trade specialization |
| `is_active` | boolean | Whether user is active |
| `created_at` | string | ISO datetime of creation |
| `updated_at` | string | ISO datetime of last update |

## ⚠️ Validation Rules

- **limit**: Must be between 1 and 1000
- **offset**: Must be 0 or greater
- **user_id**: Can be any string, invalid IDs return empty results (not errors)

## 🔄 Pagination Guide

To implement pagination:

1. **First page**: `get_users(limit=20, offset=0)`
2. **Second page**: `get_users(limit=20, offset=20)`
3. **Third page**: `get_users(limit=20, offset=40)`
4. **Continue**: `offset = page_number * limit`

## 🆚 vs search_users

| Feature | get_users | search_users |
|---------|-----------|-------------|
| **Purpose** | Simple retrieval | Complex searching |
| **Parameters** | 4 simple params | 9+ search criteria |
| **Complexity** | Low | High |
| **Use Case** | Listing, pagination | Filtering, finding |
| **Performance** | Optimized for speed | Optimized for flexibility |

## 🛠️ Integration

This tool is automatically available in your MCP server once the file is in place. It will appear as `get_users` in the available tools list.

### LangGraph Agent Usage
```python
# In your agent configuration
tools = [*get_db_mcp_tools()]  # get_users will be included automatically

# Usage in agent prompts
"Use get_users to retrieve user information with simple parameters"
```

## 🔧 Maintenance Notes

- **Database Connection**: Uses shared `get_db_connection()` from mcp_init
- **Error Handling**: Comprehensive error handling with detailed messages
- **Performance**: Optimized query with proper indexing on is_active and names
- **Data Types**: Handles MySQL datetime and boolean conversion automatically

## 📈 Performance Considerations

- **Sorting**: Results sorted by active status first, then alphabetically
- **Indexing**: Ensure database has indexes on `is_active`, `first_name`, `last_name`
- **Limits**: Default limit of 50 prevents accidentally large responses
- **Pagination**: Proper OFFSET/LIMIT implementation for efficient pagination

---

*This tool was created as part of the TiDB Hackathon MCP Database Server project.*