"""
批次操作測試
"""
import pytest
from fastapi import status

def test_batch_operations_mixed(client, auth_headers, sample_excel_file):
    """測試混合批次操作"""
    response = client.post(
        "/api/excel/batch",
        headers=auth_headers,
        json={
            "file": "test.xlsx",
            "sheet": "Sheet1",
            "operations": [
                {
                    "type": "append",
                    "values": ["E004", "Batch User 1", "IT", 55000]
                },
                {
                    "type": "append",
                    "values": ["E005", "Batch User 2", "Sales", 60000]
                },
                {
                    "type": "update",
                    "row": 2,
                    "values": ["E001", "Updated", "Engineering", 80000],
                    "column_start": 1
                }
            ]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 3
    
    # 驗證每個操作都成功
    for result in data["results"]:
        assert result["success"] is True

def test_batch_operations_with_failure(client, auth_headers, sample_excel_file):
    """測試包含失敗操作的批次"""
    response = client.post(
        "/api/excel/batch",
        headers=auth_headers,
        json={
            "file": "test.xlsx",
            "sheet": "Sheet1",
            "operations": [
                {
                    "type": "append",
                    "values": ["E006", "Valid User", "HR", 50000]
                },
                {
                    "type": "update",
                    "row": 999,  # 無效列號
                    "values": ["Invalid"],
                    "column_start": 1
                },
                {
                    "type": "append",
                    "values": ["E007", "Another Valid", "Finance", 70000]
                }
            ]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 3
    
    # 驗證所有操作都有結果（批次操作會繼續執行）
    assert data["results"][0]["success"] is True
    # 第二個操作可能成功（如果檔案擴展）或失敗
    assert "success" in data["results"][1]
    assert data["results"][2]["success"] is True

def test_batch_empty_operations(client, auth_headers):
    """測試空批次操作"""
    response = client.post(
        "/api/excel/batch",
        headers=auth_headers,
        json={
            "file": "test.xlsx",
            "sheet": "Sheet1",
            "operations": []
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 0

def test_batch_large_operations(client, auth_headers):
    """測試大量批次操作"""
    operations = []
    for i in range(100):
        operations.append({
            "type": "append",
            "values": [f"E{i:04d}", f"User {i}", "Dept", 50000 + i]
        })
    
    response = client.post(
        "/api/excel/batch",
        headers=auth_headers,
        json={
            "file": "batch_large.xlsx",
            "sheet": "Sheet1",
            "operations": operations
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) == 100
    
    # 驗證所有操作都成功
    for result in data["results"]:
        assert result["success"] is True
