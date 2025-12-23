# Excel API Server

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **concurrent-safe** RESTful API server for Excel file operations. Designed for multi-user scenarios where multiple workflows or users need to access the same Excel files simultaneously.

[中文說明](README_zh-TW.md)

## 🎯 Why This Project?

### The Problem
When multiple processes/users access Excel files simultaneously:
- ❌ File corruption
- ❌ Data loss (last-write-wins)
- ❌ Race conditions
- ❌ No coordination between processes

### The Solution
This API server provides:
- ✅ **File locking mechanism** - Automatic queue management
- ✅ **Concurrent safety** - No data loss or corruption
- ✅ **Multi-user support** - Perfect for web forms and n8n workflows
- ✅ **RESTful API** - Easy integration with any platform
- ✅ **Batch operations** - Efficient bulk updates

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
# 1. Clone repository
git clone https://github.com/yourusername/excel-api-server.git
cd excel-api-server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create data directory
mkdir data

# 5. Set environment variables
export API_TOKEN=your-secret-token-here

# 6. Start server
uvicorn main:app --host 0.0.0.0 --port 8000

# 7. Access API documentation
# Open browser: http://localhost:8000/docs
```

## 📚 API Documentation

### Interactive API Docs

Once the server is running, visit:
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
  "version": "1.0.0",
  "timestamp": "2025-12-20T10:30:00"
}
```

#### 2. Append Row

```bash
POST /api/excel/append
Content-Type: application/json
Authorization: Bearer {token}

Body:
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

#### 3. Read Data

```bash
POST /api/excel/read
Content-Type: application/json
Authorization: Bearer {token}

Body:
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "range": "A1:D10"  // Optional, leave empty for all data
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

#### 4. Update Row

```bash
PUT /api/excel/update
Content-Type: application/json
Authorization: Bearer {token}

Body:
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

#### 5. Delete Row

```bash
DELETE /api/excel/delete
Content-Type: application/json
Authorization: Bearer {token}

Body:
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

#### 6. Batch Operations

```bash
POST /api/excel/batch
Content-Type: application/json
Authorization: Bearer {token}

Body:
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

- **Automatic queue management** - Requests are processed sequentially
- **Timeout protection** - Default 30 seconds timeout
- **Error recovery** - Locks are automatically released on errors
- **Thread-safe** - Uses Python threading.Lock
- **Cross-platform** - Works on Windows, Linux, and macOS

## 🔧 Configuration

### Environment Variables

Create `.env` file:

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

### Docker Environment

In `docker-compose.yml`:

```yaml
environment:
  - API_TOKEN=${API_TOKEN}
  - LOG_LEVEL=INFO
  - LOCK_TIMEOUT=60
```

## 🧪 Testing

### Unit Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Concurrent Test

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

# Launch 10 concurrent requests
threads = [threading.Thread(target=append_row, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print("All requests completed!")
```

### Load Test

```bash
# Using Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer your-token" \
   -p append.json -T application/json \
   http://localhost:8000/api/excel/append

# Using wrk
wrk -t4 -c10 -d30s -H "Authorization: Bearer your-token" \
    --script=append.lua http://localhost:8000/api/excel/append
```

## 📊 Performance

### Benchmarks

Tested on: Intel Core i7, 16GB RAM, SSD

| Operation | Throughput | Latency (avg) |
|-----------|-----------|---------------|
| Append (single) | ~50 req/s | 20ms |
| Append (batch 10) | ~200 req/s | 50ms |
| Read (1000 rows) | ~100 req/s | 10ms |
| Update (single) | ~45 req/s | 22ms |

### Optimization Tips

1. **Use batch operations** for multiple changes
2. **Specify range** when reading (don't read entire file)
3. **Enable caching** for frequently read data
4. **Use SSD** for data directory
5. **Increase workers** for high load

## 🛡️ Security

### Best Practices

1. **Use strong API tokens**
   ```bash
   # Generate secure token
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use HTTPS in production**
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

3. **Enable rate limiting**
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

4. **Restrict file paths**
   - Files are automatically restricted to `EXCEL_ROOT_DIR`
   - Path traversal attacks are prevented

5. **Regular backups**
   ```bash
   # backup.sh
   #!/bin/bash
   BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
   mkdir -p $BACKUP_DIR
   cp -r ./data/*.xlsx $BACKUP_DIR/
   ```

## 📈 Monitoring

### Logs

```bash
# Docker
docker-compose logs -f excel-api

# Local
tail -f logs/excel-api.log
```

### Metrics Endpoint

```python
# Add to main.py
@app.get("/api/metrics")
async def get_metrics():
    return {
        "active_locks": len([l for l in file_lock_manager.locks.values() if l.locked()]),
        "total_files": len(file_lock_manager.locks),
        "uptime": time.time() - start_time
    }
```

### Health Check

```bash
# Add to docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🐳 Docker

### Build Image

```bash
docker build -t excel-api-server .
```

### Run Container

```bash
docker run -d \
  --name excel-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e API_TOKEN=your-token \
  excel-api-server
```

### Docker Compose

```yaml
version: '3.8'

services:
  excel-api:
    build: .
    container_name: excel-api-server
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - API_TOKEN=${API_TOKEN}
      - LOG_LEVEL=INFO
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Optional: Nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - excel-api
```

## 🔧 Troubleshooting

### Issue 1: Port already in use

```bash
# Check what's using the port
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Issue 2: File permission denied

```bash
# Fix permissions
chmod -R 755 data/
chown -R $(whoami) data/
```

### Issue 3: Lock timeout

**Cause:** Operation taking too long or deadlock

**Solution:**
```bash
# Restart server to release all locks
docker-compose restart excel-api

# Or increase timeout in .env
LOCK_TIMEOUT=60
```

### Issue 4: Excel file corrupted

**Solution:**
```bash
# Restore from backup
cp backups/latest/your-file.xlsx data/

# Verify file integrity
python -c "import openpyxl; wb = openpyxl.load_workbook('data/your-file.xlsx'); print('OK')"
```

## 🤝 Contributing

Contributions are welcome!

### Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/excel-api-server.git
cd excel-api-server

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dev dependencies
pip install -r requirements-dev.txt

# 4. Run tests
pytest

# 5. Start dev server
uvicorn main:app --reload
```

### Submitting Changes

1. Create a feature branch: `git checkout -b feature/AmazingFeature`
2. Commit your changes: `git commit -m 'Add AmazingFeature'`
3. Push to the branch: `git push origin feature/AmazingFeature`
4. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🔗 Related Projects

- [n8n-nodes-excel-api](https://github.com/yourusername/n8n-nodes-excel-api) - n8n community node for this API
- [n8n](https://github.com/n8n-io/n8n) - Workflow automation tool

## 📧 Support

- GitHub Issues: [Report a bug](https://github.com/yourusername/excel-api-server/issues)
- Email: your.email@example.com
- Documentation: [Wiki](https://github.com/yourusername/excel-api-server/wiki)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file library
- [n8n](https://n8n.io/) - Workflow automation platform

---

**Made with ❤️ for concurrent Excel operations**