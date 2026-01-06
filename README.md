# Excel API Server

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.4.0-blue.svg)](CHANGELOG.md)

一個**並發安全**的 Excel 檔案操作 RESTful API 伺服器。專為多使用者場景設計，讓多個工作流程或使用者可以同時安全地存取相同的 Excel 檔案。支援批量條件更新和刪除，完美適用於自動化工作流程。

## 📖 文件導航

- **[快速開始](#-快速開始)** - 立即開始使用
- **[API 文件](#-api-文件)** - 完整的 API 端點說明
- **[API 參數參考](API_REFERENCE.md)** - 詳細的參數說明和範例
- **[測試指南](TESTING.md)** - 如何執行測試
- **[版本歷史](CHANGELOG.md)** - 完整的更新記錄
- **[v3.4.0 更新說明](RELEASE_NOTES_3.4.0.md)** - 最新版本的新功能

## 🎯 為什麼需要這個專案？

### 問題
當多個程序/使用者同時存取 Excel 檔案時：
- ❌ 檔案損壞
- ❌ 資料遺失（最後寫入覆蓋）
- ❌ 競態條件（Race conditions）
- ❌ 程序間缺乏協調

### 解決方案
本 API 伺服器提供：
- ✅ **檔案鎖定機制** - 自動佇列管理
- ✅ **並發安全** - 無資料遺失或損壞
- ✅ **多使用者支援** - 完美適用於 Web 表單和 n8n 工作流程
- ✅ **RESTful API** - 易於與任何平台整合
- ✅ **批次操作** - 高效的批量更新

## 🚀 快速開始

### 方法 1：Docker（建議）

```bash
# 1. 建立 docker-compose.yml
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

# 2. 啟動服務
docker-compose up -d

# 3. 測試
curl http://localhost:8000/
```

### 方法 2：Python 虛擬環境

```bash
# 1. 複製儲存庫
git clone https://github.com/code4Copilot/excel-api-server.git
cd excel-api-server

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows 系統使用：venv\Scripts\activate

# 3. 安裝相依套件
pip install -r requirements.txt

# 4. 建立資料目錄
mkdir data

# 5. 設定環境變數
export API_TOKEN=your-secret-token-here

# 6. 啟動伺服器
uvicorn main:app --host 0.0.0.0 --port 8000

# 7. 存取 API 文件
# 在瀏覽器中開啟：http://localhost:8000/docs
```

## 📚 API 文件

### 互動式 API 文件

伺服器啟動後，請造訪：
- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### 身分驗證

所有 API 請求都需要 Bearer token 驗證：

```bash
curl -X POST http://localhost:8000/api/excel/append \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"file": "test.xlsx", "sheet": "Sheet1", "values": ["A", "B", "C"]}'
```

### API 端點

#### 1. 健康檢查

```bash
GET /

回應：
{
  "service": "Excel API Server",
  "status": "running",
  "version": "3.4.0",
  "timestamp": "2026-01-06T10:30:00"
}
```

#### 2. 新增列

```bash
POST /api/excel/append
Content-Type: application/json
Authorization: Bearer {token}

請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "values": ["E0001", "John Doe", "Engineering", 75000]
}

回應：
{
  "success": true,
  "row_number": 5,
  "message": "Row appended successfully at row 5"
}
```

#### 3. 讀取資料

```bash
POST /api/excel/read
Content-Type: application/json
Authorization: Bearer {token}

請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "range": "A1:D10"  // 選填，留空則讀取所有資料
}

回應：
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

#### 4. 更新列

```bash
PUT /api/excel/update
Content-Type: application/json
Authorization: Bearer {token}

請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5,
  "values": ["E0001", "John Smith", "Sales", 80000],
  "column_start": 1
}

回應：
{
  "success": true,
  "message": "Row 5 updated successfully"
}
```

#### 5. 刪除列

```bash
DELETE /api/excel/delete
Content-Type: application/json
Authorization: Bearer {token}

請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}

回應：
{
  "success": true,
  "message": "Row 5 deleted successfully"
}
```

#### 6. 進階更新（支援條件查詢和批量更新）

```bash
PUT /api/excel/update_advanced
Content-Type: application/json
Authorization: Bearer {token}

# 範例 1：按列號更新（單筆）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 3,
  "values_to_set": {
    "Name": "Updated Name",
    "Salary": 85000
  }
}

回應：
{
  "success": true,
  "message": "1 row(s) updated",
  "rows_updated": [3],
  "updated_count": 1,
  "updated_columns": ["Name", "Salary"]
}

# 範例 2：按條件查詢更新（批量 - 所有符合記錄）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": true,  // 預設為 true，處理所有符合條件的記錄
  "values_to_set": {
    "Salary": 90000
  }
}

回應：
{
  "success": true,
  "message": "3 row(s) updated",
  "rows_updated": [2, 5, 8],
  "updated_count": 3,
  "updated_columns": ["Salary"],
  "process_mode": "all"
}

# 範例 3：按條件查詢更新（僅第一筆）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": false,  // 設為 false，只處理第一筆符合的記錄
  "values_to_set": {
    "Salary": 90000
  }
}

回應：
{
  "success": true,
  "message": "1 row(s) updated",
  "rows_updated": [2],
  "updated_count": 1,
  "updated_columns": ["Salary"],
  "process_mode": "first"
}
```

**功能特色：**
- 🎯 **按列號更新**：使用 `row` 參數更新指定列
- 🔍 **條件查詢**：使用 `lookup_column` 和 `lookup_value` 查找記錄
- 📦 **批量更新**：使用 `process_all=true`（預設）更新所有符合條件的記錄
- 🎯 **單筆更新**：使用 `process_all=false` 只更新第一筆符合的記錄
- 🎨 **欄位選擇**：只更新 `values_to_set` 中指定的欄位
- 🛡️ **標題保護**：無法更新第 1 列（標題列）

#### 7. 進階刪除（支援條件查詢和批量刪除）

```bash
DELETE /api/excel/delete_advanced
Content-Type: application/json
Authorization: Bearer {token}

# 範例 1：按列號刪除（單筆）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}

回應：
{
  "success": true,
  "message": "1 row(s) deleted",
  "rows_deleted": [5],
  "deleted_count": 1
}

# 範例 2：按條件查詢刪除（批量 - 所有符合記錄）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": true  // 預設為 true，刪除所有符合條件的記錄
}

回應：
{
  "success": true,
  "message": "4 row(s) deleted",
  "rows_deleted": [8, 6, 4, 2],
  "deleted_count": 4,
  "process_mode": "all"
}

# 範例 3：按條件查詢刪除（僅第一筆）
請求內容：
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": false  // 設為 false，只刪除第一筆符合的記錄
}

回應：
{
  "success": true,
  "message": "1 row(s) deleted",
  "rows_deleted": [2],
  "deleted_count": 1,
  "process_mode": "first"
}
```

**功能特色：**
- 🎯 **按列號刪除**：使用 `row` 參數刪除指定列
- 🔍 **條件查詢**：使用 `lookup_column` 和 `lookup_value` 查找記錄
- 📦 **批量刪除**：使用 `process_all=true`（預設）刪除所有符合條件的記錄
- 🎯 **單筆刪除**：使用 `process_all=false` 只刪除第一筆符合的記錄
- ⚡ **智能排序**：從後往前刪除，避免行號偏移
- 🛡️ **標題保護**：無法刪除第 1 列（標題列）

#### 8. 批次操作

```bash
POST /api/excel/batch
Content-Type: application/json
Authorization: Bearer {token}

請求內容：
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

回應：
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

## � 批量操作使用案例

### 案例 1：批量更新員工薪資

```python
import requests

API_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer your-token"}

# 將所有 Engineering 部門員工的薪資調整為 90000
response = requests.put(
    f"{API_URL}/api/excel/update_advanced",
    headers=HEADERS,
    json={
        "file": "employees.xlsx",
        "sheet": "Sheet1",
        "lookup_column": "Department",
        "lookup_value": "Engineering",
        "process_all": True,  # 預設值，處理所有符合條件的記錄
        "values_to_set": {
            "Salary": 90000,
            "LastUpdate": "2026-01-05"
        }
    }
)

result = response.json()
print(f"已更新 {result['updated_count']} 位員工")
print(f"更新的列號: {result['rows_updated']}")
```

### 案例 2：批量刪除過期訂單

```python
# 刪除所有狀態為 "已取消" 的訂單
response = requests.request(
    "DELETE",
    f"{API_URL}/api/excel/delete_advanced",
    headers=HEADERS,
    json={
        "file": "orders.xlsx",
        "sheet": "Orders",
        "lookup_column": "Status",
        "lookup_value": "已取消",
        "process_all": True  # 預設值，刪除所有符合條件的訂單
    }
)

result = response.json()
print(f"已刪除 {result['deleted_count']} 筆訂單")
```

### 案例 3：只更新第一筆符合條件的記錄

```python
# 適用於需要只處理第一筆匹配記錄的場景
# 例如：處理待處理的客服工單（先進先出）
response = requests.put(
    f"{API_URL}/api/excel/update_advanced",
    headers=HEADERS,
    json={
        "file": "support_tickets.xlsx",
        "sheet": "Tickets",
        "lookup_column": "Status",
        "lookup_value": "待處理",
        "process_all": False,  # 只處理第一筆
        "values_to_set": {
            "Status": "處理中",
            "AssignedTo": "Agent001",
            "StartTime": "2026-01-06 10:00:00"
        }
    }
)

result = response.json()
if result['success']:
    print(f"已指派工單 (列 {result['rows_updated'][0]})")
    print(f"處理模式: {result['process_mode']}")  # 輸出: "first"
```

### 案例 4：條件篩選與更新

```python
# 步驟 1：讀取所有資料
read_response = requests.post(
    f"{API_URL}/api/excel/read",
    headers=HEADERS,
    json={"file": "products.xlsx", "sheet": "Sheet1"}
)

data = read_response.json()["data"]
headers = data[0]

# 步驟 2：分析並批量更新
# 將所有庫存低於 10 的商品標記為 "需補貨"
for row in data[1:]:
    product_id = row[0]
    stock = row[3]  # 假設庫存在第 4 欄
    
    if stock < 10:
        requests.put(
            f"{API_URL}/api/excel/update_advanced",
            headers=HEADERS,
            json={
                "file": "products.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "ProductID",
                "lookup_value": product_id,
                "values_to_set": {"Status": "需補貨"}
            }
        )
```

### 案例 5：n8n 工作流程整合

在 n8n 中使用 Excel API 節點：

**範例 1：批量更新所有匹配記錄（預設行為）**
```javascript
// n8n HTTP Request 節點設定
{
  "method": "PUT",
  "url": "http://excel-api:8000/api/excel/update_advanced",
  "authentication": "genericCredentialType",
  "headers": {
    "Authorization": "Bearer {{$credentials.apiToken}}"
  },
  "body": {
    "file": "{{$node["Get File"].json["file"]}}",
    "sheet": "Sheet1",
    "lookup_column": "Email",
    "lookup_value": "{{$json["email"]}}",
    "process_all": true,  // 預設值，更新所有匹配的記錄
    "values_to_set": {
      "LastLogin": "{{$now}}",
      "Status": "Active"
    }
  }
}
```

**範例 2：只處理第一筆匹配記錄（適用於工單處理等場景）**
```javascript
// n8n HTTP Request 節點設定 - 處理待辦工單
{
  "method": "PUT",
  "url": "http://excel-api:8000/api/excel/update_advanced",
  "authentication": "genericCredentialType",
  "headers": {
    "Authorization": "Bearer {{$credentials.apiToken}}"
  },
  "body": {
    "file": "tickets.xlsx",
    "sheet": "Tickets",
    "lookup_column": "Status",
    "lookup_value": "待處理",
    "process_all": false,  // 只處理第一筆待處理工單
    "values_to_set": {
      "Status": "處理中",
      "AssignedTo": "{{$json["agent_id"]}}",
      "StartTime": "{{$now}}"
    }
  }
}
```

**優勢：**
- ✅ 彈性控制：可選擇處理所有記錄或只處理第一筆
- ✅ 單次 API 調用處理多筆記錄（process_all=true）
- ✅ 先進先出處理（process_all=false 適用於佇列場景）
- ✅ 減少網路往返次數
- ✅ 原子性操作，確保資料一致性
- ✅ 自動處理並發安全

## �🔒 檔案鎖定機制

### 運作原理

```python
# 請求 1 到達
鎖定檔案 → 讀取 Excel → 修改 → 寫入 Excel → 釋放鎖定

# 請求 2 到達（當請求 1 正在處理時）
等待鎖定 → 鎖定檔案 → 讀取 Excel → 修改 → 寫入 Excel → 釋放鎖定

# 請求 3 到達（當請求 2 正在處理時）
等待鎖定 → ...
```

### 功能特色

- **自動佇列管理** - 請求會依序處理
- **逾時保護** - 預設 30 秒逾時
- **錯誤復原** - 發生錯誤時會自動釋放鎖定
- **執行緒安全** - 使用 Python threading.Lock
- **跨平台** - 支援 Windows、Linux 和 macOS

## 🔧 設定

### 環境變數

建立 `.env` 檔案：

```env
# API 安全性
API_TOKEN=your-super-secret-token-change-in-production

# 伺服器設定
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Excel 設定
EXCEL_ROOT_DIR=./data
MAX_FILE_SIZE_MB=50

# 效能
LOCK_TIMEOUT=30
MAX_WORKERS=4
```

### Docker 環境

在 `docker-compose.yml` 中：

```yaml
environment:
  - API_TOKEN=${API_TOKEN}
  - LOG_LEVEL=INFO
  - LOCK_TIMEOUT=60
```

## 🧪 測試

### 單元測試

```bash
# 執行所有測試
pytest

# 執行並產生覆蓋率報告
pytest --cov=. --cov-report=html
```

### 並發測試

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

# 啟動 10 個並發請求
threads = [threading.Thread(target=append_row, args=(i,)) for i in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print("所有請求完成！")
```

### 負載測試

```bash
# 使用 Apache Bench
ab -n 100 -c 10 -H "Authorization: Bearer your-token" \
   -p append.json -T application/json \
   http://localhost:8000/api/excel/append

# 使用 wrk
wrk -t4 -c10 -d30s -H "Authorization: Bearer your-token" \
    --script=append.lua http://localhost:8000/api/excel/append
```

## 📊 效能

### 基準測試

測試環境：Intel Core i7、16GB RAM、SSD

| 操作 | 吞吐量 | 延遲（平均）|
|-----------|-----------|---------------|
| 新增（單筆）| ~50 req/s | 20ms |
| 新增（批次 10 筆）| ~200 req/s | 50ms |
| 讀取（1000 列）| ~100 req/s | 10ms |
| 更新（單筆）| ~45 req/s | 22ms |

### 最佳化建議

1. **使用批次操作**進行多筆變更
2. **指定範圍**進行讀取（不要讀取整個檔案）
3. **啟用快取**用於經常讀取的資料
4. **使用 SSD** 作為資料目錄
5. **增加工作程序數**以應對高負載

## 🛡️ 安全性

### 最佳實踐

1. **使用強式 API token**
   ```bash
   # 產生安全的 token
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **在正式環境使用 HTTPS**
   ```nginx
   # Nginx 反向代理
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

3. **啟用速率限制**
   ```python
   # 在 main.py 中
   from slowapi import Limiter
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/api/excel/append")
   @limiter.limit("100/minute")
   async def append_row(...):
       pass
   ```

4. **限制檔案路徑**
   - 檔案會自動限制在 `EXCEL_ROOT_DIR` 目錄內
   - 可防止路徑遍歷攻擊

5. **定期備份**
   ```bash
   # backup.sh
   #!/bin/bash
   BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
   mkdir -p $BACKUP_DIR
   cp -r ./data/*.xlsx $BACKUP_DIR/
   ```

## 📈 監控

### 日誌

```bash
# Docker
docker-compose logs -f excel-api

# 本機
tail -f logs/excel-api.log
```

### 指標端點

```python
# 加入到 main.py
@app.get("/api/metrics")
async def get_metrics():
    return {
        "active_locks": len([l for l in file_lock_manager.locks.values() if l.locked()]),
        "total_files": len(file_lock_manager.locks),
        "uptime": time.time() - start_time
    }
```

### 健康檢查

```bash
# 加入到 docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## 🐳 Docker

### 建置映像檔

```bash
docker build -t excel-api-server .
```

### 執行容器

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

  # 選填：Nginx 反向代理
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

## 🔧 故障排除

### 問題 1：埠號已被使用

```bash
# 檢查是什麼在使用該埠號
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# 在 docker-compose.yml 中變更埠號
ports:
  - "8001:8000"
```

### 問題 2：檔案權限被拒絕

```bash
# Fix permissions
chmod -R 755 data/
chown -R $(whoami) data/
```

### 問題 3：鎖定逾時

**原因：** 操作時間過長或死鎖

**解決方案：**
```bash
# 重新啟動伺服器以釋放所有鎖定
docker-compose restart excel-api

# 或在 .env 中增加逾時時間
LOCK_TIMEOUT=60
```

### 問題 4：Excel 檔案損壞

**解決方案：**
```bash
# 從備份還原
cp backups/latest/your-file.xlsx data/

# 驗證檔案完整性
python -c "import openpyxl; wb = openpyxl.load_workbook('data/your-file.xlsx'); print('OK')"
```

## 🤝 貢獻

歡迎貢獻！

### 開發環境設定

```bash
# 1. Fork 並 clone
git clone https://github.com/code4Copilot/excel-api-server.git
cd excel-api-server

# 2. 建立虛擬環境
python -m venv venv
source venv/bin/activate

# 3. 安裝開發相依套件
pip install -r requirements-dev.txt

# 4. 執行測試
pytest

# 5. 啟動開發伺服器
uvicorn main:app --reload
```

### 提交變更

1. 建立功能分支：`git checkout -b feature/AmazingFeature`
2. 提交你的變更：`git commit -m 'Add AmazingFeature'`
3. 推送到分支：`git push origin feature/AmazingFeature`
4. 開啟 Pull Request

## 📄 授權條款

MIT License - 詳見 [LICENSE](LICENSE) 檔案

## � 更新日誌

### Version 3.4.0 (2026-01-06)

**新功能：**
- ✨ 新增 `process_all` 參數到進階更新 API (`/api/excel/update_advanced`)
  - `process_all=true` (預設): 處理所有符合條件的記錄
  - `process_all=false`: 只處理第一筆符合條件的記錄
- ✨ 新增 `process_all` 參數到進階刪除 API (`/api/excel/delete_advanced`)
  - `process_all=true` (預設): 刪除所有符合條件的記錄
  - `process_all=false`: 只刪除第一筆符合條件的記錄
- 🎯 回應中新增 `process_mode` 欄位，顯示 "all" 或 "first"

**改進：**
- 📚 完善 API 文件，新增 `process_all` 參數使用範例
- 🧪 新增針對 `process_all` 參數的單元測試
- 📖 更新 README.md 和 TESTING.md 文件

**相容性：**
- ✅ 完全向後相容：`process_all` 預設為 `true`，保持原有行為
- ✅ 適用於 n8n 社群節點的 Process Mode 選項

### Version 3.3.0 及更早版本
詳見 [CHANGELOG.md](CHANGELOG.md)

## �🔗 相關專案

- [n8n-nodes-excel-api](https://github.com/code4Copilot/n8n-nodes-excel-api) - 此 API 的 n8n 社群節點
- [n8n](https://github.com/n8n-io/n8n) - 工作流程自動化工具

## 📧 支援

- GitHub Issues：[回報問題](https://github.com/code4Copilot/excel-api-server/issues)
- Email：your.email@example.com
- 文件：[Wiki](https://github.com/code4Copilot/excel-api-server/wiki)

## 🙏 致謝

- [FastAPI](https://fastapi.tiangolo.com/) - 現代化的 Python Web 框架
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel 檔案函式庫
- [n8n](https://n8n.io/) - 工作流程自動化平台

---

**用 ❤️ 為並發 Excel 操作而製作**