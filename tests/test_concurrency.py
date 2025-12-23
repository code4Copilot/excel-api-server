"""
並發安全測試
"""
import pytest
import threading
import time
from fastapi import status

@pytest.mark.slow
def test_concurrent_appends(client, auth_headers):
    """測試並發新增操作"""
    NUM_THREADS = 10
    results = []
    
    def append_row(thread_id):
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": "concurrent_test.xlsx",
                "sheet": "Sheet1",
                "values": [f"T{thread_id:03d}", f"User {thread_id}", "Dept", 50000]
            }
        )
        results.append(response.status_code == status.HTTP_200_OK)
    
    # 啟動多個執行緒
    threads = []
    for i in range(NUM_THREADS):
        t = threading.Thread(target=append_row, args=(i,))
        threads.append(t)
        t.start()
    
    # 等待所有執行緒完成
    for t in threads:
        t.join()
    
    # 驗證所有請求都成功
    assert all(results), "Some concurrent requests failed"
    assert len(results) == NUM_THREADS
    
    # 驗證資料完整性
    response = client.post(
        "/api/excel/read",
        headers=auth_headers,
        json={
            "file": "concurrent_test.xlsx",
            "sheet": "Sheet1"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # 應該有 NUM_THREADS 列資料
    assert data["row_count"] == NUM_THREADS

@pytest.mark.slow
def test_concurrent_mixed_operations(client, auth_headers, sample_excel_file):
    """測試並發混合操作"""
    NUM_THREADS = 5
    results = {"append": [], "read": [], "update": []}
    
    def append_op(thread_id):
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "values": [f"T{thread_id}", f"Thread {thread_id}", "Dept", 50000]
            }
        )
        results["append"].append(response.status_code == status.HTTP_200_OK)
    
    def read_op():
        response = client.post(
            "/api/excel/read",
            headers=auth_headers,
            json={"file": "test.xlsx", "sheet": "Sheet1"}
        )
        results["read"].append(response.status_code == status.HTTP_200_OK)
    
    def update_op(row_num):
        response = client.put(
            "/api/excel/update",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "row": row_num,
                "values": ["Updated", "Updated", "Updated", 99999],
                "column_start": 1
            }
        )
        results["update"].append(response.status_code == status.HTTP_200_OK)
    
    threads = []
    for i in range(NUM_THREADS):
        threads.append(threading.Thread(target=append_op, args=(i,)))
        threads.append(threading.Thread(target=read_op))
        threads.append(threading.Thread(target=update_op, args=(2,)))
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    # 驗證所有操作都成功
    assert all(results["append"]), "Some append operations failed"
    assert all(results["read"]), "Some read operations failed"
    assert all(results["update"]), "Some update operations failed"

def test_lock_timeout(client, auth_headers, monkeypatch, clean_test_env):
    """測試鎖定超時機制"""
    # 設定較短的超時時間
    from main import file_lock_manager
    original_timeout = file_lock_manager.default_timeout
    file_lock_manager.default_timeout = 2.0
    
    try:
        # 手動獲取鎖定（使用完整路徑）
        test_file = "timeout_test.xlsx"
        test_file_path = str(clean_test_env / test_file)
        file_lock_manager.acquire(test_file_path)
        
        # 嘗試在超時時間內執行操作
        start_time = time.time()
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": test_file,
                "sheet": "Sheet1",
                "values": ["Test", "Data"]
            }
        )
        elapsed = time.time() - start_time
        
        # 應該在超時時間後失敗（返回 500 因為鎖定超時被當作內部錯誤處理）
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert elapsed >= 2.0
        
    finally:
        # 恢復原設定並釋放鎖定
        file_lock_manager.default_timeout = original_timeout
        file_lock_manager.release(test_file_path)

@pytest.mark.slow
def test_concurrent_file_creation(client, auth_headers):
    """測試並發建立多個檔案"""
    NUM_FILES = 5
    results = []
    
    def create_file(file_id):
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": f"file_{file_id}.xlsx",
                "sheet": "Sheet1",
                "values": [f"Data{file_id}", "Test", "Dept", 50000]
            }
        )
        results.append(response.status_code == status.HTTP_200_OK)
    
    threads = []
    for i in range(NUM_FILES):
        t = threading.Thread(target=create_file, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    # 驗證所有檔案都成功建立
    assert all(results), "Some file creations failed"
    
    # 驗證所有檔案都存在
    response = client.get("/api/excel/files", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["count"] >= NUM_FILES
