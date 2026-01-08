# API 參數快速參考

## 獲取表頭 API (`GET /api/excel/headers`)

### 請求參數

| 參數名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `file` | string | ✅ | - | Excel 檔案名稱 |
| `sheet` | string | ❌ | "Sheet1" | 工作表名稱 |

### 回應欄位

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `success` | boolean | 操作是否成功 |
| `headers` | array | 表頭欄位名稱列表 |
| `count` | integer | 表頭欄位數量 |

### 使用範例

#### 範例 1：獲取預設工作表的表頭
```json
{
  "file": "users.xlsx"
}
```

**回應：**
```json
{
  "success": true,
  "headers": ["ID", "Name", "Department", "Salary"],
  "count": 4
}
```

#### 範例 2：獲取指定工作表的表頭
```json
{
  "file": "sales.xlsx",
  "sheet": "Q1Sales"
}
```

**回應：**
```json
{
  "success": true,
  "headers": ["Date", "Product", "Amount", "Region"],
  "count": 4
}
```

### 使用場景

- 🎯 **前端下拉選單**：動態生成欄位選項
- 🔍 **表單驗證**：驗證使用者輸入的欄位名稱
- 🛠️ **資料導入**：標題匹配與映射
- 📊 **資料探索**：了解 Excel 檔案結構

---

## 進階更新 API (`PUT /api/excel/update_advanced`)

### 請求參數

| 參數名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `file` | string | ✅ | - | Excel 檔案名稱 |
| `sheet` | string | ❌ | "Sheet1" | 工作表名稱 |
| `row` | integer | 條件式* | - | 直接指定列號 (1-based，從 2 開始) |
| `lookup_column` | string | 條件式* | - | 查找的欄位名稱（表頭） |
| `lookup_value` | string | 條件式* | - | 查找的值 |
| `process_all` | boolean | ❌ | `true` | **v3.4.0 新增**<br>• `true`: 處理所有符合條件的記錄<br>• `false`: 只處理第一筆符合條件的記錄 |
| `values_to_set` | object | ✅ | - | 要更新的欄位與值 (key: 欄位名稱, value: 新值) |

\* 必須提供 `row` 或 (`lookup_column` + `lookup_value`) 其中一種定位方式

### 回應欄位

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `success` | boolean | 操作是否成功 |
| `message` | string | 操作結果訊息 |
| `rows_updated` | array | 更新的列號列表 |
| `updated_count` | integer | 更新的記錄數 |
| `updated_columns` | array | 更新的欄位列表 |
| `process_mode` | string | **v3.4.0 新增**<br>• "all": 處理了所有匹配記錄<br>• "first": 只處理了第一筆記錄 |

### 使用範例

#### 範例 1：按列號更新（單筆）
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

#### 範例 2：批量更新（所有符合條件的記錄）
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

#### 範例 3：單筆更新（只處理第一筆）
```json
{
  "file": "tickets.xlsx",
  "sheet": "Tickets",
  "lookup_column": "Status",
  "lookup_value": "待處理",
  "process_all": false,
  "values_to_set": {
    "Status": "處理中",
    "AssignedTo": "Agent001"
  }
}
```

---

## 進階刪除 API (`DELETE /api/excel/delete_advanced`)

### 請求參數

| 參數名稱 | 類型 | 必填 | 預設值 | 說明 |
|---------|------|------|--------|------|
| `file` | string | ✅ | - | Excel 檔案名稱 |
| `sheet` | string | ❌ | "Sheet1" | 工作表名稱 |
| `row` | integer | 條件式* | - | 直接指定列號 (1-based，從 2 開始) |
| `lookup_column` | string | 條件式* | - | 查找的欄位名稱（表頭） |
| `lookup_value` | string | 條件式* | - | 查找的值 |
| `process_all` | boolean | ❌ | `true` | **v3.4.0 新增**<br>• `true`: 刪除所有符合條件的記錄<br>• `false`: 只刪除第一筆符合條件的記錄 |

\* 必須提供 `row` 或 (`lookup_column` + `lookup_value`) 其中一種定位方式

### 回應欄位

| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `success` | boolean | 操作是否成功 |
| `message` | string | 操作結果訊息 |
| `rows_deleted` | array | 刪除的列號列表（按刪除順序，從後往前） |
| `deleted_count` | integer | 刪除的記錄數 |
| `process_mode` | string | **v3.4.0 新增**<br>• "all": 刪除了所有匹配記錄<br>• "first": 只刪除了第一筆記錄 |

### 使用範例

#### 範例 1：按列號刪除（單筆）
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "row": 5
}
```

#### 範例 2：批量刪除（所有符合條件的記錄）
```json
{
  "file": "users.xlsx",
  "sheet": "Sheet1",
  "lookup_column": "Department",
  "lookup_value": "Sales",
  "process_all": true
}
```

#### 範例 3：單筆刪除（只刪除第一筆）
```json
{
  "file": "orders.xlsx",
  "sheet": "Orders",
  "lookup_column": "Status",
  "lookup_value": "已取消",
  "process_all": false
}
```

---

## process_all 參數使用指南

### 何時使用 `process_all: true` (預設)
- ✅ 批量更新所有符合條件的記錄
- ✅ 清理所有過期或無效的資料
- ✅ 統一調整某類別的所有記錄
- ✅ 數據遷移或批量修正

**範例場景：**
- 將所有 Engineering 部門員工的薪資統一調整
- 刪除所有狀態為"已取消"的訂單
- 更新所有過期產品的狀態

### 何時使用 `process_all: false`
- ✅ 先進先出 (FIFO) 處理佇列
- ✅ 單一任務分配（如工單系統）
- ✅ 限制資源使用（一次只處理一筆）
- ✅ 避免意外批量操作

**範例場景：**
- 從待處理工單佇列中取出第一筆進行處理
- 分配下一筆未處理的客服案件給客服人員
- 處理排程任務（一次執行一個）
- 測試或驗證環境中謹慎操作

### 最佳實踐

1. **明確指定參數**
   - 即使使用預設值，也建議明確指定 `process_all` 參數
   - 讓 API 調用意圖更清晰

2. **驗證操作範圍**
   - 使用 `/api/excel/read` 先檢查會影響哪些記錄
   - 查看回應中的 `updated_count` 或 `deleted_count`

3. **日誌記錄**
   - 記錄 `process_mode` 和影響的列號
   - 便於追蹤和問題排查

4. **測試環境先試**
   - 先在測試檔案上驗證操作結果
   - 確認符合預期後再用於生產資料

---

## 錯誤處理

### 常見錯誤碼

| 狀態碼 | 說明 | 解決方案 |
|--------|------|----------|
| 400 | 無效的請求參數 | 檢查參數格式和必填欄位 |
| 401 | 認證失敗 | 檢查 Bearer Token |
| 404 | 檔案或記錄不存在 | 確認檔案名稱和查詢條件 |
| 503 | 檔案被鎖定 | 等待其他操作完成或增加超時時間 |
| 500 | 伺服器內部錯誤 | 查看伺服器日誌 |

### 錯誤回應範例

```json
{
  "detail": "No row found where Department = NonExistent"
}
```

---

## 相容性說明

### v3.4.0 向後相容性
- ✅ 所有舊版 API 調用無需修改
- ✅ `process_all` 參數為可選，預設值為 `true`
- ✅ 新增的 `process_mode` 欄位不影響現有邏輯
- ✅ 與 n8n 社群節點 v1.1.0+ 完全相容

### 升級建議
1. 檢視現有 API 調用
2. 識別需要單筆處理的場景
3. 添加 `process_all: false` 參數
4. 測試並驗證結果
5. 更新文件和程式碼註解

---

**更新日期：** 2026-01-06  
**API 版本：** 3.4.0
