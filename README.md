# Excel API Server

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.4.2-blue.svg)](CHANGELOG.md)

A **concurrency-safe** RESTful API server for Excel file operations. Designed for multi-user scenarios, allowing multiple workflows or users to safely access the same Excel files simultaneously. Supports batch conditional updates and deletions, perfect for automation workflows.

## 📖 Documentation Navigation

- **[Quick Start](#-quick-start)** - Get started immediately
- **[API Documentation](#-api-documentation)** - Complete API endpoint reference
- **[API Parameter Reference](API_REFERENCE.md)** - Detailed parameter descriptions and examples
- **[Testing Guide](TESTING.md)** - How to run tests
- **[Changelog](CHANGELOG.md)** - Complete update history
- **[v3.4.2 Release Notes](RELEASE_NOTES_3.4.2.md)** - Latest version improvements
- **[中文文檔](README_zh-tw.md)** - Chinese version

## 🎯 Why This Project?

### The Problem
When multiple processes/users access Excel files simultaneously:
- ❌ File corruption
- ❌ Data loss (last write wins)
- ❌ Race conditions
- ❌ Lack of coordination between processes

### The Solution
This API server provides:
- ✅ **File Locking Mechanism** - Automatic queue management
- ✅ **Concurrency Safe** - No data loss or corruption
- ✅ **Multi-user Support** - Perfect for web forms and n8n workflows
- ✅ **RESTful API** - Easy integration with any platform
- ✅ **Batch Operations** - Efficient bulk updates

## 🚀 Quick Start

### Method 1: Docker (Recommended)

```bash
# 1. Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  excel-api:
    image: yourusername/excel-api-server:latest
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - API_TOKEN=your-secret-token-here
    restart: unless-stopped
EOF

# 2. Start the service
docker-compose up -d

# 3. Test
curl http://localhost:8000/
```

### Method 2: Python Virtual Environment

```bash
# 1. Clone the repository
git clone https://github.com/code4Copilot/excel-api-server.git
cd excel-api-server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create data directory
mkdir data

# 5. Set environment variable
export API_TOKEN=your-secret-token-here

# 6. Start the server
uvicorn main:app --host 0.0.0.0 --port 8000

# 7. Access API documentation
# Open in browser: http://localhost:8000/docs
```

## 📚 API Documentation

### Interactive API Documentation

After starting the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Authentication

All API requests require Bearer token authentication:

```bash
curl -X POST http://localhost:8000/api/excel/append \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"file": "test.xlsx", "sheet": "Sheet1", "values": ["A", "B", "C"]}'
```

### API Endpoints

#### 1. Health Check

```bash
GET /

Response:
{
  "service": "Excel API Server",
  "status": "running",
  "version": "3.4.1",
  "timestamp": "2026-01-08T10:30:00"
}
```

#### 2. List Sheets

```bash
GET /api/excel/sheets?file=users.xlsx
Authorization: Bearer {token}

Response:
{
  "success": true,
  "sheets": ["Sheet1", "Sheet2"]
}
```

#### 3. Get Headers

```bash
GET /api/excel/headers?file=users.xlsx&sheet=Sheet1
Authorization: Bearer {token}

Response:
{
  "success": true,
  "headers": ["ID", "Name", "Department", "Salary"],
  "count": 4
}
```

**Use Cases:**
- 🎯 For frontend dropdown menus
- 🔍 Dynamic form field generation
- ✅ Validate column names
- 📊 Data structure exploration

#### 4. Append Row

```bash
POST /api/excel/append
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "values": ["E0001", "John Doe", "Engineering", 75000]
}

Response:
{
  "success": true,
  "row_number": 5,
  "message": "Row appended successfully at row 5"
}
```

#### 5. Read Data

```bash
POST /api/excel/read
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "range": "A1:D10"  // Optional, leave empty to read all data
}

Response:
{
  "success": true,
  "data": [
    ["ID", "Name", "Department", "Salary"],
    ["E0001", "John Doe", "Engineering", 75000],
    ...
  ],
  "row_count": 10
}
```

#### 6. Update Row

```bash
PUT /api/excel/update
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5,
  "values": ["E0001", "John Smith", "Sales", 80000],
  "column_start": 1
}

Response:
{
  "success": true,
  "message": "Row 5 updated successfully"
}
```

#### 7. Delete Row

```bash
DELETE /api/excel/delete
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}

Response:
{
  "success": true,
  "message": "Row 5 deleted successfully"
}
```

#### 8. Advanced Update (Supports conditional queries and batch updates)

```bash
PUT /api/excel/update_advanced
Content-Type: application/json
Authorization: Bearer {token}

# Example 1: Update by row number (single record)
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 3,
  "values_to_set": {
    "Name": "Updated Name",
    "Salary": 85000
  }
}

Response:
{
  "success": true,
  "message": "1 row(s) updated",
  "rows_updated": [3],
  "updated_count": 1,
  "updated_columns": ["Name", "Salary"]
}

# Example 2: Conditional batch update (all matching records)
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": true,  // Default true, processes all matching records
  "values_to_set": {
    "Salary": 90000
  }
}

Response:
{
  "success": true,
  "message": "3 row(s) updated",
  "rows_updated": [2, 5, 8],
  "updated_count": 3,
  "updated_columns": ["Salary"],
  "process_mode": "all"
}

# Example 3: Update first matching record only
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": false,  // Set to false to process only first match
  "values_to_set": {
    "Salary": 90000
  }
}

Response:
{
  "success": true,
  "message": "1 row(s) updated",
  "rows_updated": [2],
  "updated_count": 1,
  "updated_columns": ["Salary"],
  "process_mode": "first"
}
```

**Features:**
- 🎯 **Update by Row Number**: Use `row` parameter to update specific row
- 🔍 **Conditional Queries**: Use `lookup_column` and `lookup_value` to find records
- 📦 **Batch Updates**: Use `process_all=true` (default) to update all matching records
- 🎯 **Single Update**: Use `process_all=false` to update only first match
- 🎨 **Column Selection**: Only update columns specified in `values_to_set`
- 🛡️ **Header Protection**: Cannot update row 1 (header row)

#### 9. Advanced Delete (Supports conditional queries and batch deletion)

```bash
DELETE /api/excel/delete_advanced
Content-Type: application/json
Authorization: Bearer {token}

# Example 1: Delete by row number (single record)
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}

Response:
{
  "success": true,
  "message": "1 row(s) deleted",
  "rows_deleted": [5],
  "deleted_count": 1
}

# Example 2: Conditional batch delete (all matching records)
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": true  // Default true, deletes all matching records
}

Response:
{
  "success": true,
  "message": "4 row(s) deleted",
  "rows_deleted": [8, 6, 4, 2],
  "deleted_count": 4,
  "process_mode": "all"
}

# Example 3: Delete first matching record only
Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": false  // Set to false to delete only first match
}

Response:
{
  "success": true,
  "message": "1 row(s) deleted",
  "rows_deleted": [2],
  "deleted_count": 1,
  "process_mode": "first"
}
```

**Features:**
- 🎯 **Delete by Row Number**: Use `row` parameter to delete specific row
- 🔍 **Conditional Queries**: Use `lookup_column` and `lookup_value` to find records
- 📦 **Batch Deletion**: Use `process_all=true` (default) to delete all matching records
- 🎯 **Single Deletion**: Use `process_all=false` to delete only first match
- ⚡ **Smart Ordering**: Deletes from bottom to top to avoid row offset issues
- 🛡️ **Header Protection**: Cannot delete row 1 (header row)

#### 10. Batch Operations

```bash
POST /api/excel/batch
Content-Type: application/json
Authorization: Bearer {token}

Request Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "operations": [
    {
      "type": "append",
      "values": ["E0010", "Alice", "Marketing", 65000]
    },
    {
      "type": "update",
      "row": 5,
      "values": ["E0005", "Updated", "IT", 90000]
    },
    {
      "type": "delete",
      "row": 10
    }
  ]
}

Response:
{
  "success": true,
  "results": [
    {"operation": "append", "success": true, "row_number": 11},
    {"operation": "update", "success": true, "row": 5},
    {"operation": "delete", "success": true, "row": 10}
  ],
  "total_operations": 3
}
```

## 💡 Batch Operation Use Cases

### Case 1: Batch Update Employee Salaries

```python
import requests

API_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer your-token"}

# Update all Engineering department employees' salary to 90000
response = requests.put(
    f"{API_URL}/api/excel/update_advanced",
    headers=HEADERS,
    json={
        "file": "employees.xlsx",
        "sheet": "Sheet1",
        "lookup_column": "Department",
        "lookup_value": "Engineering",
        "process_all": True,  # Default value, process all matching records
        "values_to_set": {
            "Salary": 90000,
            "LastUpdate": "2026-01-08"
        }
    }
)

result = response.json()
print(f"Updated {result['updated_count']} employees")
print(f"Updated rows: {result['rows_updated']}")
```

### Case 2: Batch Delete Expired Orders

```python
# Delete all orders with status "Cancelled"
response = requests.request(
    "DELETE",
    f"{API_URL}/api/excel/delete_advanced",
    headers=HEADERS,
    json={
        "file": "orders.xlsx",
        "sheet": "Orders",
        "lookup_column": "Status",
        "lookup_value": "Cancelled",
        "process_all": True  # Default value, delete all matching orders
    }
)

result = response.json()
print(f"Deleted {result['deleted_count']} orders")
```

### Case 3: Update Only First Matching Record

```python
# Suitable for scenarios requiring only first match processing
# Example: Process pending support tickets (FIFO)
response = requests.put(
    f"{API_URL}/api/excel/update_advanced",
    headers=HEADERS,
    json={
        "file": "support_tickets.xlsx",
        "sheet": "Tickets",
        "lookup_column": "Status",
        "lookup_value": "Pending",
        "process_all": False,  # Process only first match
        "values_to_set": {
            "Status": "In Progress",
            "AssignedTo": "Agent001",
            "StartTime": "2026-01-08 10:00:00"
        }
    }
)

result = response.json()
if result['success']:
    print(f"Assigned ticket (row {result['rows_updated'][0]})")
    print(f"Process mode: {result['process_mode']}")  # Output: "first"
```

## 🔒 File Locking Mechanism

### How It Works

```python
# Request 1 arrives
Lock file → Read Excel → Modify → Write Excel → Release lock

# Request 2 arrives (while Request 1 is processing)
Wait for lock → Lock file → Read Excel → Modify → Write Excel → Release lock

# Request 3 arrives (while Request 2 is processing)
Wait for lock → ...
```

### Features

- **Automatic Queue Management** - Requests are processed sequentially
- **Timeout Protection** - Default 30-second timeout
- **Error Recovery** - Automatically releases lock on errors
- **Thread Safe** - Uses Python threading.Lock
- **Cross-platform** - Supports Windows, Linux, and macOS

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
# API Security
API_TOKEN=your-super-secret-token-change-in-production

# Server Settings
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Excel Settings
EXCEL_ROOT_DIR=./data
MAX_FILE_SIZE_MB=50

# Performance
LOCK_TIMEOUT=30
MAX_WORKERS=4
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Concurrency Test

```python
# concurrent_test.py
import requests
import threading

API_URL = "http://localhost:8000"
TOKEN = "your-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def append_row(worker_id):
    response = requests.post(
        f"{API_URL}/api/excel/append",
        headers=HEADERS,
        json={
            "file": "test.xlsx",
            "sheet": "Sheet1",
            "values": [f"Worker-{worker_id}", "Data", 123]
        }
    )
    print(f"Worker {worker_id}: {response.json()}")

# Start 10 concurrent requests
threads = [threading.Thread(target=append_row, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print("All requests completed!")
```

## 📊 Performance

### Benchmarks

Test Environment: Intel Core i7, 16GB RAM, SSD

| Operation | Throughput | Latency (Avg) |
|-----------|-----------|---------------|
| Append (single) | ~50 req/s | 20ms |
| Append (batch 10) | ~200 req/s | 50ms |
| Read (1000 rows) | ~100 req/s | 10ms |
| Update (single) | ~45 req/s | 22ms |

## 🛡️ Security

### Best Practices

1. **Use Strong API Token**
   ```bash
   # Generate secure token
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use HTTPS in Production**
   ```nginx
   # Nginx reverse proxy
   server {
       listen 443 ssl;
       server_name api.yourdomain.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable Rate Limiting**
   ```python
   # In main.py
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/api/excel/append")
   @limiter.limit("100/minute")
   async def append_row(...):
       pass
   ```

## 📄 License

MIT License - See [LICENSE](LICENSE) file

## 📋 Changelog

### Version 3.4.1 (2026-01-08)

**New Features:**
- ✨ Added `/api/excel/headers` endpoint
  - Get headers (first row) of specified worksheet
  - Returns list of column names
  - For frontend dropdowns and dynamic forms
  - Uses read_only mode for better performance

**Improvements:**
- 📚 Complete documentation for headers endpoint
- 🧪 Added unit tests for headers endpoint
- 📖 Updated README.md and API_REFERENCE.md
- 🌍 Added English documentation

### Version 3.4.0 (2026-01-06)

**New Features:**
- ✨ Added `process_all` parameter to Advanced Update API (`/api/excel/update_advanced`)
  - `process_all=true` (default): Process all matching records
  - `process_all=false`: Process only first matching record
- ✨ Added `process_all` parameter to Advanced Delete API (`/api/excel/delete_advanced`)
  - `process_all=true` (default): Delete all matching records
  - `process_all=false`: Delete only first matching record
- 🎯 Added `process_mode` field in response, showing "all" or "first"

**Improvements:**
- 📚 Enhanced API documentation with `process_all` parameter examples
- 🧪 Added unit tests for `process_all` parameter
- 📖 Updated README.md and TESTING.md documentation

**Compatibility:**
- ✅ Fully backward compatible: `process_all` defaults to `true`, maintaining original behavior
- ✅ Compatible with n8n community node Process Mode option

### Version 3.3.0 and Earlier
See [CHANGELOG.md](CHANGELOG.md)

## 🔗 Related Projects

- [n8n-nodes-excel-api](https://github.com/code4Copilot/n8n-nodes-excel-api) - n8n community node for this API
- [n8n](https://github.com/n8n-io/n8n) - Workflow automation tool

## 📧 Support

- GitHub Issues: [Report Issues](https://github.com/code4Copilot/excel-api-server/issues)
- Email: your.email@example.com
- Documentation: [Wiki](https://github.com/code4Copilot/excel-api-server/wiki)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file library
- [n8n](https://n8n.io/) - Workflow automation platform

---

**Made with ❤️ for Concurrent Excel Operations**
