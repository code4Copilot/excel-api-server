# API Parameter Quick Reference

## Get Headers API (`GET /api/excel/headers`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | string | ✅ | - | Excel file name |
| `sheet` | string | ❌ | "Sheet1" | Worksheet name |

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether operation was successful |
| `headers` | array | List of header column names |
| `count` | integer | Number of header columns |

### Usage Examples

#### Example 1: Get headers from default worksheet
```json
{
  "file": "users.xlsx"
}
```

**Response:**
```json
{
  "success": true,
  "headers": ["ID", "Name", "Department", "Salary"],
  "count": 4
}
```

#### Example 2: Get headers from specific worksheet
```json
{
  "file": "sales.xlsx",
  "sheet": "Q1Sales"
}
```

**Response:**
```json
{
  "success": true,
  "headers": ["Date", "Product", "Amount", "Region"],
  "count": 4
}
```

### Use Cases

- 🎯 **Frontend Dropdowns**: Dynamically generate column options
- 🔍 **Form Validation**: Validate user input column names
- 🛠️ **Data Import**: Header matching and mapping
- 📊 **Data Exploration**: Understand Excel file structure

---

## Advanced Update API (`PUT /api/excel/update_advanced`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | string | ✅ | - | Excel file name |
| `sheet` | string | ❌ | "Sheet1" | Worksheet name |
| `row` | integer | Conditional* | - | Direct row number (1-based, starting from 2) |
| `lookup_column` | string | Conditional* | - | Column name to search (header) |
| `lookup_value` | string | Conditional* | - | Value to search for |
| `process_all` | boolean | ❌ | `true` | **v3.4.0 New**<br>• `true`: Process all matching records<br>• `false`: Process only first matching record |
| `values_to_set` | object | ✅ | - | Fields and values to update (key: field name, value: new value) |

\* Must provide either `row` or (`lookup_column` + `lookup_value`)

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether operation was successful |
| `message` | string | Operation result message |
| `rows_updated` | array | List of updated row numbers |
| `updated_count` | integer | Number of records updated |
| `updated_columns` | array | List of updated columns |
| `process_mode` | string | **v3.4.0 New**<br>• "all": Processed all matching records<br>• "first": Processed only first record |

### Usage Examples

#### Example 1: Update by row number (single record)
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 3,
  "values_to_set": {
    "Name": "Updated Name",
    "Salary": 85000
  }
}
```

#### Example 2: Batch update (all matching records)
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": true,
  "values_to_set": {
    "Salary": 90000
  }
}
```

#### Example 3: Single update (process first match only)
```json
{
  "file": "tickets.xlsx",
  "sheet": "Tickets",
  "lookup_column": "Status",
  "lookup_value": "Pending",
  "process_all": false,
  "values_to_set": {
    "Status": "In Progress",
    "AssignedTo": "Agent001"
  }
}
```

---

## Advanced Delete API (`DELETE /api/excel/delete_advanced`)

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file` | string | ✅ | - | Excel file name |
| `sheet` | string | ❌ | "Sheet1" | Worksheet name |
| `row` | integer | Conditional* | - | Direct row number (1-based, starting from 2) |
| `lookup_column` | string | Conditional* | - | Column name to search (header) |
| `lookup_value` | string | Conditional* | - | Value to search for |
| `process_all` | boolean | ❌ | `true` | **v3.4.0 New**<br>• `true`: Delete all matching records<br>• `false`: Delete only first matching record |

\* Must provide either `row` or (`lookup_column` + `lookup_value`)

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether operation was successful |
| `message` | string | Operation result message |
| `rows_deleted` | array | List of deleted row numbers (in deletion order, bottom to top) |
| `deleted_count` | integer | Number of records deleted |
| `process_mode` | string | **v3.4.0 New**<br>• "all": Deleted all matching records<br>• "first": Deleted only first record |

### Usage Examples

#### Example 1: Delete by row number (single record)
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}
```

#### Example 2: Batch delete (all matching records)
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": true
}
```

#### Example 3: Single delete (delete first match only)
```json
{
  "file": "orders.xlsx",
  "sheet": "Orders",
  "lookup_column": "Status",
  "lookup_value": "Cancelled",
  "process_all": false
}
```

---

## process_all Parameter Guide

### When to use `process_all: true` (default)
- ✅ Batch update all matching records
- ✅ Clean up all expired or invalid data
- ✅ Uniformly adjust all records of a category
- ✅ Data migration or bulk corrections

**Example Scenarios:**
- Uniformly adjust salaries for all Engineering department employees
- Delete all orders with status "Cancelled"
- Update status of all expired products

### When to use `process_all: false`
- ✅ First-In-First-Out (FIFO) queue processing
- ✅ Single task assignment (e.g., ticketing systems)
- ✅ Limit resource usage (process one at a time)
- ✅ Avoid accidental batch operations

**Example Scenarios:**
- Pick first pending ticket from queue for processing
- Assign next unprocessed support case to agent
- Process scheduled tasks (execute one at a time)
- Careful operations in test/validation environments

### Best Practices

1. **Explicitly specify parameter**
   - Even when using default value, recommend explicitly specifying `process_all`
   - Makes API call intent clearer

2. **Validate operation scope**
   - Use `/api/excel/read` to check which records will be affected first
   - Review `updated_count` or `deleted_count` in response

3. **Logging**
   - Log `process_mode` and affected row numbers
   - Facilitates tracking and troubleshooting

4. **Test in test environment first**
   - Validate operation results on test files first
   - Apply to production data after confirming expectations

---

## Error Handling

### Common Error Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| 400 | Invalid request parameters | Check parameter format and required fields |
| 401 | Authentication failed | Check Bearer Token |
| 404 | File or record not found | Verify file name and query conditions |
| 503 | File is locked | Wait for other operations to complete or increase timeout |
| 500 | Internal server error | Check server logs |

### Error Response Example

```json
{
  "detail": "No row found where Department = NonExistent"
}
```

---

## Compatibility Notes

### v3.4.0 Backward Compatibility
- ✅ All legacy API calls require no modifications
- ✅ `process_all` parameter is optional, defaults to `true`
- ✅ New `process_mode` field does not affect existing logic
- ✅ Fully compatible with n8n community node v1.1.0+

### Upgrade Recommendations
1. Review existing API calls
2. Identify scenarios requiring single-record processing
3. Add `process_all: false` parameter
4. Test and validate results
5. Update documentation and code comments

---

### v3.4.1 New Features
- ✨ Added `/api/excel/headers` endpoint for getting worksheet headers
- 📚 Returns column names list for frontend dropdowns
- ⚡ Uses read_only mode for optimal performance

---

**Last Updated:** 2026-01-08  
**API Version:** 3.4.1
