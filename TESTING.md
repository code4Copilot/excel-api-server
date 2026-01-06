# 測試指南

本專案使用 pytest 進行單元測試和整合測試，確保 Excel API Server 的功能正確性和穩定性。

## 安裝測試依賴

```bash
pip install -r requirements-dev.txt
```

## 執行測試

### 執行所有測試

```bash
# 基本執行
pytest

# 詳細輸出
pytest -v

# 顯示測試覆蓋率
pytest --cov=main --cov-report=html

# 僅執行快速測試（排除慢速測試）
pytest -m "not slow"
```

### 執行特定測試

```bash
# 執行特定檔案
pytest tests/test_api_basic.py

# 執行特定測試類別
pytest tests/test_api_crud.py::TestAppendOperations

# 執行特定測試函數
pytest tests/test_api_basic.py::test_root_endpoint

# 使用關鍵字篩選
pytest -k "append"
```

### 並發測試

```bash
# 執行並發測試（標記為 slow）
pytest -m slow tests/test_concurrency.py

# 執行並發測試並顯示詳細輸出
pytest -v -s tests/test_concurrency.py
```

### 效能測試

```bash
# 執行效能測試
pytest tests/test_performance.py -v -s

# 僅執行效能測試
pytest -m slow tests/test_performance.py
```

## 查看測試覆蓋率報告

執行測試後，查看 HTML 覆蓋率報告：

```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

或在命令列中查看摘要：

```bash
pytest --cov=main --cov-report=term-missing
```

## 測試結構

```
tests/
├── conftest.py              # pytest 配置和共用 fixtures
├── test_api_basic.py        # 基本 API 測試
├── test_api_crud.py         # CRUD 操作測試
├── test_api_batch.py        # 批次操作測試
├── test_concurrency.py      # 並發安全測試
├── test_performance.py      # 效能測試
└── test_data/              # 測試資料目錄（自動建立和清理）
```

## 測試涵蓋範圍

### 1. 基本 API 測試 (test_api_basic.py)
- ✅ 根端點測試
- ✅ 認證測試（無認證、無效 token）
- ✅ 列出檔案測試（空目錄、有檔案）
- ✅ 列出工作表測試
- ✅ 檔案不存在處理

### 2. CRUD 操作測試 (test_api_crud.py)
- ✅ 新增操作（新檔案、現有檔案、物件模式）
- ✅ 讀取操作（全部資料、特定範圍、不存在檔案）
- ✅ 更新操作（按列號、Lookup 模式、無效列）
- ✅ 進階更新操作
  - ✅ 批量更新（process_all=True，處理所有匹配記錄）
  - ✅ 單筆更新（process_all=False，只處理第一筆匹配記錄）
- ✅ 刪除操作（按列號、Lookup 模式、不存在列）
- ✅ 進階刪除操作
  - ✅ 批量刪除（process_all=True，刪除所有匹配記錄）
  - ✅ 單筆刪除（process_all=False，只刪除第一筆匹配記錄）

### 3. 批次操作測試 (test_api_batch.py)
- ✅ 混合批次操作
- ✅ 包含失敗的批次操作
- ✅ 空批次操作
- ✅ 大量批次操作（100+）

### 4. 並發測試 (test_concurrency.py)
- ✅ 並發新增操作
- ✅ 並發混合操作（新增、讀取、更新）
- ✅ 鎖定超時機制
- ✅ 並發建立多個檔案

### 5. 效能測試 (test_performance.py)
- ✅ 新增操作效能（100 次操作 < 200ms/op）
- ✅ 讀取操作效能（50 次讀取 1000 列 < 100ms/op）
- ✅ 批次操作效能
- ✅ 更新操作效能（50 次更新 < 150ms/op）

## Fixtures 說明

### test_data_dir
- 範圍：session（整個測試會話）
- 功能：建立測試資料目錄，測試結束後自動清理

### clean_test_env
- 範圍：function（每個測試函數）
- 功能：清理測試環境、設定環境變數、清除檔案鎖定

### client
- 範圍：function
- 功能：建立 FastAPI TestClient 進行 API 測試

### auth_headers
- 範圍：function
- 功能：提供認證標頭

### sample_excel_file
- 範圍：function
- 功能：建立包含測試資料的範例 Excel 檔案

## CI/CD 整合

### GitHub Actions 範例

建立 `.github/workflows/test.yml`：

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements-dev.txt
      
      - name: Run tests
        run: |
          pytest --cov=main --cov-report=xml --cov-report=term-missing
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

## 疑難排解

### 測試失敗

1. **確認依賴已安裝**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **確認測試資料目錄可寫入**
   ```bash
   # 檢查 tests/test_data 目錄權限
   ```

3. **檢查檔案鎖定問題**
   - 確認沒有其他程序佔用測試檔案
   - 重啟測試前清理 `tests/test_data/` 目錄

### 並發測試不穩定

- 增加超時時間（在 conftest.py 中調整）
- 減少並發執行緒數量
- 確認系統資源充足（CPU、記憶體）

### 效能測試失敗

- 在效能較好的機器上執行
- 調整效能閾值（在 test_performance.py 中修改 assert 條件）
- 確認沒有其他程序干擾測試
- 關閉防毒軟體的即時掃描（可能影響檔案 I/O）

### 測試覆蓋率不足

```bash
# 查看未測試的程式碼
pytest --cov=main --cov-report=term-missing

# 生成詳細的 HTML 報告
pytest --cov=main --cov-report=html
start htmlcov/index.html
```

## 最佳實踐

1. **測試隔離**：每個測試應該獨立運行，不依賴其他測試的結果
2. **清理資源**：使用 fixtures 自動清理測試資料
3. **有意義的斷言**：使用清晰的斷言訊息
4. **測試命名**：使用描述性的測試函數名稱
5. **標記慢速測試**：使用 `@pytest.mark.slow` 標記耗時測試
6. **定期執行**：在 CI/CD 流程中自動執行測試

## 撰寫新測試

當新增功能時，請遵循以下步驟：

1. 在適當的測試檔案中新增測試函數
2. 使用現有的 fixtures 或建立新的 fixtures
3. 確保測試覆蓋正常情況和邊界情況
4. 執行測試確保通過：`pytest tests/test_your_new_test.py -v`
5. 檢查測試覆蓋率：`pytest --cov=main`

範例：

```python
def test_new_feature(client, auth_headers):
    """測試新功能"""
    response = client.post(
        "/api/excel/new_feature",
        headers=auth_headers,
        json={"param": "value"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

## 效能基準

目前的效能基準（在標準開發機器上）：

- 新增操作：< 200ms/op
- 讀取操作（1000列）：< 100ms/op
- 更新操作：< 150ms/op
- 批次操作（50個）：比單獨操作快 20 倍以上

## 支援

如有測試相關問題，請：
1. 檢查本文件的疑難排解章節
2. 查看測試執行的詳細輸出：`pytest -v -s`
3. 檢查測試日誌：`logs/` 目錄
