# Excel API Server v3.4.1 Release Notes

**發布日期 / Release Date:** 2026-01-08

## 🎉 新增功能 / New Features

### 📊 Headers 端點 / Headers Endpoint

新增 `/api/excel/headers` GET 端點，用於獲取 Excel 工作表的表頭資訊。

Added `/api/excel/headers` GET endpoint to retrieve Excel worksheet headers.

**中文說明：**
- 🎯 **用途**：獲取指定工作表的第一列（表頭）
- 📋 **返回內容**：欄位名稱列表
- ⚡ **效能優化**：使用 read_only 模式讀取
- 🔒 **並發安全**：支援檔案鎖定機制

**English Description:**
- 🎯 **Purpose**: Get first row (headers) of specified worksheet
- 📋 **Returns**: List of column names
- ⚡ **Performance**: Uses read_only mode for reading
- 🔒 **Concurrency Safe**: Supports file locking mechanism

## 📝 使用範例 / Usage Examples

### 中文範例

```bash
# 獲取預設工作表的表頭
GET /api/excel/headers?file=users.xlsx
Authorization: Bearer your-token

# 獲取指定工作表的表頭
GET /api/excel/headers?file=sales.xlsx&sheet=Q1Sales
Authorization: Bearer your-token
```

**回應：**
```json
{
  "success": true,
  "headers": ["ID", "Name", "Department", "Salary"],
  "count": 4
}
```

### English Example

```bash
# Get headers from default worksheet
GET /api/excel/headers?file=users.xlsx
Authorization: Bearer your-token

# Get headers from specific worksheet
GET /api/excel/headers?file=sales.xlsx&sheet=Q1Sales
Authorization: Bearer your-token
```

**Response:**
```json
{
  "success": true,
  "headers": ["ID", "Name", "Department", "Salary"],
  "count": 4
}
```

## 🎯 使用場景 / Use Cases

### 中文

1. **前端下拉選單**
   - 動態生成欄位選項
   - 讓使用者選擇要操作的欄位

2. **表單驗證**
   - 驗證使用者輸入的欄位名稱
   - 確保欄位存在於 Excel 中

3. **資料導入**
   - 表頭匹配與映射
   - 自動識別資料結構

4. **資料探索**
   - 快速瞭解 Excel 檔案結構
   - 不需要讀取完整資料

### English

1. **Frontend Dropdowns**
   - Dynamically generate column options
   - Let users select columns to operate on

2. **Form Validation**
   - Validate user-entered column names
   - Ensure columns exist in Excel

3. **Data Import**
   - Header matching and mapping
   - Automatically identify data structure

4. **Data Exploration**
   - Quickly understand Excel file structure
   - No need to read complete data

## 🔧 技術細節 / Technical Details

### API 參數 / API Parameters

| 參數 / Parameter | 類型 / Type | 必填 / Required | 預設值 / Default | 說明 / Description |
|-----------------|-------------|----------------|-----------------|-------------------|
| `file` | string | ✅ | - | Excel 檔案名稱 / Excel file name |
| `sheet` | string | ❌ | "Sheet1" | 工作表名稱 / Worksheet name |

### 回應欄位 / Response Fields

| 欄位 / Field | 類型 / Type | 說明 / Description |
|-------------|-------------|-------------------|
| `success` | boolean | 操作是否成功 / Whether operation succeeded |
| `headers` | array | 表頭欄位列表 / List of header columns |
| `count` | integer | 表頭欄位數量 / Number of header columns |

### 錯誤處理 / Error Handling

| 狀態碼 / Status | 說明 / Description |
|----------------|-------------------|
| 200 | 成功 / Success |
| 401 | 認證失敗 / Authentication failed |
| 404 | 檔案或工作表不存在 / File or sheet not found |
| 503 | 檔案被鎖定 / File is locked |

## 🧪 測試覆蓋 / Test Coverage

新增 5 個單元測試案例 / Added 5 unit test cases:

### 中文
1. ✅ 測試正常獲取表頭
2. ✅ 測試預設工作表
3. ✅ 測試檔案不存在情況
4. ✅ 測試工作表不存在情況
5. ✅ 測試無認證訪問

### English
1. ✅ Test normal header retrieval
2. ✅ Test default worksheet
3. ✅ Test file not found scenario
4. ✅ Test worksheet not found scenario
5. ✅ Test unauthorized access

**測試結果 / Test Results:** 所有測試通過 ✅ / All tests passed ✅

## 📚 文件更新 / Documentation Updates

### 中文文件
- ✅ 更新 README.md
- ✅ 更新 API_REFERENCE.md
- ✅ 更新 CHANGELOG.md
- ✅ 新增本發布說明

### English Documentation
- ✅ Created README_EN.md
- ✅ Created API_REFERENCE_EN.md
- ✅ Updated CHANGELOG.md
- ✅ Created this release note

## 🔄 相容性 / Compatibility

### 向後相容 / Backward Compatibility
- ✅ **完全相容** / **Fully Compatible**
- ✅ 不影響現有 API / Does not affect existing APIs
- ✅ 新增功能為獨立端點 / New feature is independent endpoint
- ✅ 無需修改現有代碼 / No need to modify existing code

### 升級建議 / Upgrade Recommendations
- 直接升級，無需變更 / Direct upgrade, no changes needed
- 可選擇性使用新端點 / Optional use of new endpoint
- 建議閱讀文件瞭解新功能 / Recommend reading docs to understand new features

## 🚀 快速開始 / Quick Start

### Python 範例 / Python Example

```python
import requests

API_URL = "http://localhost:8000"
TOKEN = "your-token"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# 獲取表頭 / Get headers
response = requests.get(
    f"{API_URL}/api/excel/headers",
    params={"file": "users.xlsx", "sheet": "Sheet1"},
    headers=HEADERS
)

result = response.json()
if result['success']:
    headers = result['headers']
    print(f"Column names: {headers}")
    # 輸出 / Output: Column names: ['ID', 'Name', 'Department', 'Salary']
```

### JavaScript/Node.js 範例 / JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';
const TOKEN = 'your-token';

// 獲取表頭 / Get headers
async function getHeaders() {
  const response = await axios.get(
    `${API_URL}/api/excel/headers`,
    {
      params: { file: 'users.xlsx', sheet: 'Sheet1' },
      headers: { 'Authorization': `Bearer ${TOKEN}` }
    }
  );
  
  const { success, headers, count } = response.data;
  if (success) {
    console.log(`Found ${count} columns:`, headers);
    // 輸出 / Output: Found 4 columns: ['ID', 'Name', 'Department', 'Salary']
  }
}

getHeaders();
```

### n8n 工作流程 / n8n Workflow

```json
{
  "nodes": [
    {
      "name": "Get Excel Headers",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "GET",
        "url": "http://excel-api:8000/api/excel/headers",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "qs": {
          "file": "users.xlsx",
          "sheet": "Sheet1"
        }
      }
    }
  ]
}
```

## 💡 最佳實踐 / Best Practices

### 中文

1. **快取表頭**
   - 表頭通常不會經常變動
   - 可以快取結果減少 API 調用

2. **錯誤處理**
   - 檢查 `success` 欄位
   - 處理檔案或工作表不存在的情況

3. **效能優化**
   - headers 端點使用 read_only 模式，效能優異
   - 優先使用此端點而非讀取完整資料

### English

1. **Cache Headers**
   - Headers typically don't change frequently
   - Can cache results to reduce API calls

2. **Error Handling**
   - Check `success` field
   - Handle file or worksheet not found scenarios

3. **Performance Optimization**
   - headers endpoint uses read_only mode, excellent performance
   - Prefer this endpoint over reading complete data

## 🔗 相關連結 / Related Links

- [完整文件 / Full Documentation](README_zh-tw.md)
- [API 參考 / API Reference](API_REFERENCE_zh-tw.md)
- [English Documentation](README.md)
- [English API Reference](API_REFERENCE.md)
- [測試指南 / Testing Guide](TESTING.md)
- [更新日誌 / Changelog](CHANGELOG.md)

## 📞 支援 / Support

### 中文
如有問題或建議，請：
- 提交 GitHub Issue
- 查看文件
- 聯繫開發團隊

### English
For issues or suggestions:
- Submit GitHub Issue
- Check documentation
- Contact development team

---

**感謝使用 Excel API Server！**  
**Thank you for using Excel API Server!**

Made with ❤️ for Concurrent Excel Operations
