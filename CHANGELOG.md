# 更新日誌

本文件記錄 Excel API Server 的所有重要變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/)，
版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [3.4.2] - 2026-01-08

### 改進
- 統一所有 API 的錯誤訊息格式為 `"Sheet '{sheet_name}' not found"`
- 修改 Update 和 Delete API 行為：當工作表不存在時返回 404 錯誤，而非自動建立新工作表
- 改善異常處理：確保 404 錯誤正確傳播，不被一般異常處理器覆蓋
- 新增針對錯誤訊息驗證的單元測試
  - test_read_nonexistent_sheet
  - test_update_nonexistent_sheet
  - test_delete_nonexistent_sheet

### 修正
- 修復 `read_rows()` 函數的異常處理順序，確保 HTTPException 優先處理
- 修復 Update/Delete API 會意外建立不存在工作表的問題

### 破壞性變更
- ⚠️ Update 和 Delete API 不再自動建立不存在的工作表
- 建議：使用前先確認工作表存在，或使用 Create API 明確建立

### 相容性
- ✅ Read 和 Headers API 行為不變
- ✅ 所有錯誤訊息格式統一，更易於解析
- ⚠️ 需要更新依賴 Update/Delete 自動建立工作表行為的程式碼

## [3.4.1] - 2026-01-08

### 新增
- 新增 `/api/excel/headers` API 端點
  - 獲取指定工作表的表頭（第一列）
  - 返回欄位名稱列表
  - 供前端下拉選單和動態表單使用
  - 使用 read_only 模式提高效能
- 新增英文版文件 (README_EN.md, API_REFERENCE_EN.md)

### 改進
- 完善 headers 端點的 API 文件
- 新增針對 headers 端點的完整單元測試
  - 測試正常獲取表頭
  - 測試預設工作表
  - 測試檔案不存在
  - 測試工作表不存在
  - 測試無認證訪問
- 更新 README.md 添加 headers 端點使用說明
- 更新 API_REFERENCE.md 添加 headers 參數參考

### 相容性
- ✅ 完全向後相容：不影響現有 API
- ✅ 新增功能為獨立端點

## [3.4.0] - 2026-01-06

### 新增
- 新增 `process_all` 參數到 `/api/excel/update_advanced` API
  - `process_all=true` (預設值): 處理所有符合條件的記錄
  - `process_all=false`: 只處理第一筆符合條件的記錄
- 新增 `process_all` 參數到 `/api/excel/delete_advanced` API
  - `process_all=true` (預設值): 刪除所有符合條件的記錄
  - `process_all=false`: 只刪除第一筆符合條件的記錄
- API 回應中新增 `process_mode` 欄位
  - 顯示 "all" 表示處理所有匹配記錄
  - 顯示 "first" 表示只處理第一筆記錄

### 改進
- 完善 API 文件，新增 `process_all` 參數的使用範例
- 新增針對 `process_all=false` 的單元測試案例
- 更新 README.md 添加單筆處理的使用案例
- 更新 TESTING.md 記錄新增的測試項目
- 新增 CHANGELOG.md 記錄版本歷史

### 修正
- 移除測試中對不存在的舊版 API 端點的引用

### 相容性
- ✅ 完全向後相容：所有現有 API 調用無需修改
- ✅ 預設行為保持不變（process_all 預設為 true）
- ✅ 支援 n8n 社群節點的 Process Mode 功能

## [3.3.0] - 2025-12-20

### 新增
- 進階更新 API (`/api/excel/update_advanced`)
  - 支援按列號更新
  - 支援按條件查詢批量更新
  - 支援欄位選擇性更新
- 進階刪除 API (`/api/excel/delete_advanced`)
  - 支援按列號刪除
  - 支援按條件查詢批量刪除
  - 智能從後往前刪除避免行號偏移

### 改進
- 標題列保護：無法更新或刪除第 1 列
- 批量操作回應中新增詳細資訊
  - `rows_updated`: 更新的列號列表
  - `rows_deleted`: 刪除的列號列表
  - `updated_count`: 更新的記錄數
  - `deleted_count`: 刪除的記錄數

## [3.2.0] - 2025-11-15

### 新增
- 新增物件模式的 append API (`/api/excel/append_object`)
  - 根據欄位名稱自動對應到正確位置
  - 支援部分欄位新增
- 新增批次操作 API (`/api/excel/batch`)
  - 支援混合操作類型
  - 原子性操作保證

### 改進
- 優化檔案鎖定機制
- 改進錯誤處理和日誌記錄
- 新增操作超時保護

## [3.1.0] - 2025-10-10

### 新增
- 列出檔案 API (`/api/excel/files`)
- 列出工作表 API (`/api/excel/sheets`)
- 健康檢查端點優化

### 改進
- 完善並發測試覆蓋率
- 新增性能測試基準
- Docker 映像優化

## [3.0.0] - 2025-09-01

### 新增
- 🎉 初始版本發布
- 基本 CRUD 操作 (Create, Read, Update, Delete)
- 檔案鎖定機制確保並發安全
- Bearer Token 認證
- Docker 支援
- 完整的測試套件
- API 互動式文件 (Swagger UI)

### 功能
- Excel 檔案並發安全存取
- 多使用者支援
- RESTful API 設計
- 自動檔案管理
- 錯誤處理和日誌記錄

---

## 版本號規則

- **主版號 (Major)**: 不相容的 API 變更
- **次版號 (Minor)**: 向後相容的功能新增
- **修訂號 (Patch)**: 向後相容的問題修正

## 支援與貢獻

- GitHub Issues: [回報問題](https://github.com/code4Copilot/excel-api-server/issues)
- Pull Requests: 歡迎貢獻！
- 文件: [README.md](README.md)
