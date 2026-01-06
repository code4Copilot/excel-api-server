# Version 3.4.0 更新說明

## 概述

Excel API Server v3.4.0 版本新增了 `process_all` 參數，提供更靈活的記錄處理控制，特別適用於 n8n 社群節點的 Process Mode 功能。

---

## 🎯 新功能

### 1. process_all 參數

為進階更新和刪除 API 新增 `process_all` 參數：

| API 端點 | 新增參數 | 預設值 | 說明 |
|---------|---------|--------|------|
| `PUT /api/excel/update_advanced` | `process_all` | `true` | 控制是否處理所有匹配記錄 |
| `DELETE /api/excel/delete_advanced` | `process_all` | `true` | 控制是否刪除所有匹配記錄 |

### 2. process_mode 回應欄位

API 回應中新增 `process_mode` 欄位：
- `"all"`: 處理了所有匹配的記錄
- `"first"`: 只處理了第一筆匹配的記錄

---

## 📝 使用方式

### 批量處理（預設行為）

```json
{
  "file": "users.xlsx",
  "lookup_column": "Department",
  "lookup_value": "Engineering",
  "process_all": true,  // 或省略，預設為 true
  "values_to_set": {
    "Salary": 90000
  }
}
```

**結果：** 更新所有 Engineering 部門的員工薪資

### 單筆處理（新功能）

```json
{
  "file": "tickets.xlsx",
  "lookup_column": "Status",
  "lookup_value": "待處理",
  "process_all": false,  // 只處理第一筆
  "values_to_set": {
    "Status": "處理中"
  }
}
```

**結果：** 只更新第一筆待處理的工單

---

## 🎨 適用場景

### process_all = true（批量模式）

✅ **適用場景：**
- 批量數據更新
- 清理過期或無效資料
- 統一調整某類別的所有記錄
- 數據遷移或修正

📋 **實際案例：**
- 將所有特定部門員工的薪資調整
- 刪除所有已取消的訂單
- 更新所有過期產品的狀態
- 批量修改配置參數

### process_all = false（單筆模式）

✅ **適用場景：**
- 先進先出 (FIFO) 佇列處理
- 單一任務分配（工單、案件）
- 限制資源使用
- 謹慎操作避免誤刪

📋 **實際案例：**
- 從待處理工單佇列取出一筆處理
- 分配下一個客服案件給客服人員
- 處理排程任務（一次一個）
- 測試環境中的謹慎操作

---

## 🔄 與 n8n 整合

### n8n 社群節點設定

在 n8n-nodes-excel-api v1.1.0+ 中：

1. **Update 節點**
   - 新增 "Process Mode" 選項
   - "All Matching Records" → `process_all: true`
   - "First Match Only" → `process_all: false`

2. **Delete 節點**
   - 同樣的 "Process Mode" 選項
   - 控制刪除行為

### 工作流程範例

```javascript
// n8n HTTP Request 節點
{
  "method": "PUT",
  "url": "http://excel-api:8000/api/excel/update_advanced",
  "body": {
    "file": "support_tickets.xlsx",
    "lookup_column": "Status",
    "lookup_value": "待處理",
    "process_all": false,  // 只處理第一筆
    "values_to_set": {
      "Status": "處理中",
      "AssignedTo": "{{$json["agent_id"]}}"
    }
  }
}
```

---

## ✅ 相容性

### 完全向後相容

- ✅ 所有現有 API 調用無需修改
- ✅ `process_all` 參數為可選
- ✅ 預設值保持原有行為（`true`）
- ✅ 新增欄位不影響現有邏輯

### 升級步驟

1. **無需修改現有程式碼**
   - 所有現有 API 調用繼續正常運作
   
2. **選擇性啟用新功能**
   - 識別需要單筆處理的場景
   - 添加 `process_all: false` 參數
   
3. **測試驗證**
   - 在測試環境驗證新行為
   - 確認符合預期後部署

---

## 📚 更新的文件

所有相關文件已更新以反映新功能：

1. **[README.md](README.md)**
   - 更新 API 範例
   - 新增使用案例
   - 更新 n8n 整合說明
   - 添加版本資訊

2. **[CHANGELOG.md](CHANGELOG.md)** ✨ 新增
   - 完整版本歷史
   - 詳細變更記錄

3. **[API_REFERENCE.md](API_REFERENCE.md)** ✨ 新增
   - 完整參數說明
   - 使用範例
   - 最佳實踐指南

4. **[TESTING.md](TESTING.md)**
   - 更新測試覆蓋說明
   - 新增測試案例描述

---

## 🧪 測試覆蓋

新增的測試案例：

### test_api_crud.py

1. `test_update_advanced_multiple_matches`
   - 測試 `process_all=True` 批量更新

2. `test_update_advanced_first_match_only` ✨ 新增
   - 測試 `process_all=False` 單筆更新

3. `test_delete_advanced_multiple_matches`
   - 測試 `process_all=True` 批量刪除

4. `test_delete_advanced_first_match_only` ✨ 新增
   - 測試 `process_all=False` 單筆刪除

### 測試結果

- ✅ 23/24 測試通過 (95.8%)
- ⚠️ 1 個性能測試因閾值設定而失敗（非功能性問題）
- ✅ 代碼覆蓋率：81%

---

## 🚀 部署建議

### Docker 部署

```bash
# 拉取最新版本
docker pull your-registry/excel-api-server:3.4.0

# 或重新構建
docker-compose build
docker-compose up -d
```

### 手動部署

```bash
# 更新代碼
git pull origin main

# 重啟服務
systemctl restart excel-api-server
# 或
docker-compose restart excel-api
```

### 驗證部署

```bash
# 檢查版本
curl http://localhost:8000/

# 預期回應
{
  "service": "Excel API Server",
  "status": "running",
  "version": "3.4.0",
  ...
}
```

---

## 📞 支援

### 問題回報
- GitHub Issues: https://github.com/code4Copilot/excel-api-server/issues

### 文件
- [README.md](README.md) - 完整使用指南
- [API_REFERENCE.md](API_REFERENCE.md) - API 參數參考
- [CHANGELOG.md](CHANGELOG.md) - 版本歷史
- [TESTING.md](TESTING.md) - 測試指南

### 相關專案
- [n8n-nodes-excel-api](https://github.com/code4Copilot/n8n-nodes-excel-api) - n8n 社群節點

---

**發布日期：** 2026-01-06  
**版本：** 3.4.0  
**維護者：** Excel API Server Team
