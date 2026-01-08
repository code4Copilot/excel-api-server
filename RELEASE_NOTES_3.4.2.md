# Release Notes - v3.4.2

**發布日期：2026-01-08**

## 📋 版本摘要

v3.4.2 是一個改進版本，主要統一了錯誤處理機制，提高了 API 行為的一致性和可預測性。

## 🎯 主要改進

### 1. 統一錯誤訊息格式

所有 API 端點的工作表不存在錯誤現在統一使用：
```json
{
  "detail": "Sheet 'SheetName' not found"
}
```

**影響的 API：**
- `/api/excel/read` - 讀取資料
- `/api/excel/headers` - 獲取表頭
- `/api/excel/update` - 更新資料
- `/api/excel/update_advanced` - 進階更新
- `/api/excel/delete_advanced` - 進階刪除

### 2. 修正 Update/Delete API 行為 ⚠️

**重要變更：**

之前的行為：當工作表不存在時，Update 和 Delete API 會自動建立新的工作表。

新的行為：當工作表不存在時，API 返回 `404 Not Found` 錯誤。

**原因：**
- 更安全：避免意外建立工作表
- 更可預測：行為與 Read API 一致
- 更明確：使用者需要明確使用 Create API 建立工作表

**遷移建議：**
```python
# 舊的做法（依賴自動建立）
response = requests.post(f"{API_URL}/api/excel/update", json={
    "file": "data.xlsx",
    "sheet": "NewSheet",  # 如果不存在會自動建立
    "updates": [...]
})

# 新的做法（明確檢查和建立）
try:
    response = requests.post(f"{API_URL}/api/excel/update", json={
        "file": "data.xlsx",
        "sheet": "NewSheet",
        "updates": [...]
    })
except requests.HTTPError as e:
    if e.response.status_code == 404:
        # 明確建立工作表
        create_response = requests.post(f"{API_URL}/api/excel/create", json={
            "file": "data.xlsx",
            "sheet": "NewSheet",
            "headers": ["欄位1", "欄位2"]
        })
        # 重試更新操作
        response = requests.post(f"{API_URL}/api/excel/update", ...)
```

### 3. 改善異常處理

修復了 `read_rows()` 函式的異常處理順序：
- HTTPException 現在會正確傳播，不會被一般異常處理器覆蓋
- 確保 404 錯誤正確返回，而非 500 錯誤

## 🧪 測試改進

新增了針對錯誤訊息的單元測試：
- `test_read_nonexistent_sheet` - 驗證讀取不存在工作表的錯誤訊息
- `test_update_nonexistent_sheet` - 驗證更新不存在工作表的錯誤訊息
- `test_delete_nonexistent_sheet` - 驗證刪除不存在工作表的錯誤訊息

**測試結果：**
- ✅ 42/43 測試通過
- ✅ 程式碼覆蓋率：86%
- ✅ 並發測試：4/4 通過

## ⚠️ 破壞性變更

### Update API
```python
# 之前（v3.4.1 及更早版本）
POST /api/excel/update
{
  "file": "data.xlsx",
  "sheet": "NotExist",  # 會自動建立
  "updates": [...]
}
# 回應：200 OK

# 現在（v3.4.2）
POST /api/excel/update
{
  "file": "data.xlsx",
  "sheet": "NotExist",  # 不會自動建立
  "updates": [...]
}
# 回應：404 Not Found
# {"detail": "Sheet 'NotExist' not found"}
```

### Delete API
```python
# 之前（v3.4.1 及更早版本）
POST /api/excel/delete_advanced
{
  "file": "data.xlsx",
  "sheet": "NotExist",  # 會自動建立（然後沒有資料可刪除）
  "conditions": {...}
}
# 回應：200 OK, deleted: 0

# 現在（v3.4.2）
POST /api/excel/delete_advanced
{
  "file": "data.xlsx",
  "sheet": "NotExist",  # 不會自動建立
  "conditions": {...}
}
# 回應：404 Not Found
# {"detail": "Sheet 'NotExist' not found"}
```

## 📊 相容性矩陣

| API 端點 | v3.4.1 行為 | v3.4.2 行為 | 向後相容 |
|---------|------------|------------|---------|
| Read API | 404 錯誤 | 404 錯誤 | ✅ 是 |
| Headers API | 404 錯誤 | 404 錯誤 | ✅ 是 |
| Create API | 建立工作表 | 建立工作表 | ✅ 是 |
| Update API | 自動建立 | 404 錯誤 | ⚠️ 否 |
| Delete API | 自動建立 | 404 錯誤 | ⚠️ 否 |

## 🔄 升級指南

### 步驟 1：檢查現有程式碼

搜尋所有使用 Update 或 Delete API 的程式碼：
```bash
grep -r "/api/excel/update" .
grep -r "/api/excel/delete_advanced" .
```

### 步驟 2：識別依賴自動建立的情況

檢查是否有程式碼依賴以下行為：
- 對不存在的工作表執行更新操作
- 對不存在的工作表執行刪除操作

### 步驟 3：更新程式碼

選擇以下策略之一：

**策略 A：事前檢查**
```python
# 使用 Headers API 檢查工作表是否存在
try:
    headers_response = requests.get(
        f"{API_URL}/api/excel/headers",
        params={"file": "data.xlsx", "sheet": "MySheet"}
    )
    # 工作表存在，繼續操作
except requests.HTTPError:
    # 工作表不存在，先建立
    create_sheet(...)
```

**策略 B：錯誤處理**
```python
try:
    update_response = requests.post(...)
except requests.HTTPError as e:
    if e.response.status_code == 404:
        # 建立工作表後重試
        create_sheet(...)
        update_response = requests.post(...)
    else:
        raise
```

### 步驟 4：測試

在測試環境中驗證：
1. 正常操作仍然正常
2. 不存在工作表的情況得到正確處理
3. 錯誤訊息被正確解析

## 📚 更多資源

- **[完整 API 文件](API_REFERENCE.md)** - 詳細的參數說明
- **[中文 API 文件](API_REFERENCE_zh-tw.md)** - 中文版參數說明
- **[更新日誌](CHANGELOG.md)** - 完整的版本歷史
- **[測試指南](TESTING.md)** - 如何執行測試

## 💬 回饋與支援

如果您在升級過程中遇到問題：
1. 查看 [API 文件](API_REFERENCE.md)
2. 檢視 [測試範例](tests/)
3. 提交 Issue 回報問題

---

**注意：** 此版本提高了 API 的安全性和一致性，但需要更新依賴自動建立工作表行為的程式碼。建議在生產環境部署前充分測試。
