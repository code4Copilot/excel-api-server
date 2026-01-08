"""
基本 API 端點測試
"""
import pytest
from fastapi import status

def test_root_endpoint(client):
    """測試根端點"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["service"] == "Excel API Server"
    assert data["status"] == "running"
    assert "version" in data

def test_list_files_no_auth(client):
    """測試無認證時列出檔案"""
    response = client.get("/api/excel/files")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_list_files_invalid_token(client):
    """測試無效 token"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/excel/files", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_list_files_empty(client, auth_headers):
    """測試列出空目錄"""
    response = client.get("/api/excel/files", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 0
    assert data["files"] == []

def test_list_files_with_data(client, auth_headers, sample_excel_file):
    """測試列出有檔案的目錄"""
    response = client.get("/api/excel/files", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["count"] == 1
    assert "test.xlsx" in data["files"]

def test_list_sheets(client, auth_headers, sample_excel_file):
    """測試列出工作表"""
    response = client.get(
        "/api/excel/sheets",
        params={"file": "test.xlsx"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "Sheet1" in data["sheets"]

def test_list_sheets_file_not_found(client, auth_headers):
    """測試列出不存在檔案的工作表"""
    response = client.get(
        "/api/excel/sheets",
        params={"file": "nonexistent.xlsx"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_headers(client, auth_headers, sample_excel_file):
    """測試獲取工作表表頭"""
    response = client.get(
        "/api/excel/headers",
        params={"file": "test.xlsx", "sheet": "Sheet1"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert "headers" in data
    assert data["count"] == 4
    assert data["headers"] == ["ID", "Name", "Department", "Salary"]

def test_get_headers_default_sheet(client, auth_headers, sample_excel_file):
    """測試獲取預設工作表表頭"""
    response = client.get(
        "/api/excel/headers",
        params={"file": "test.xlsx"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert len(data["headers"]) == 4

def test_get_headers_file_not_found(client, auth_headers):
    """測試獲取不存在檔案的表頭"""
    response = client.get(
        "/api/excel/headers",
        params={"file": "nonexistent.xlsx"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_headers_sheet_not_found(client, auth_headers, sample_excel_file):
    """測試獲取不存在工作表的表頭"""
    response = client.get(
        "/api/excel/headers",
        params={"file": "test.xlsx", "sheet": "NonExistentSheet"},
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "Sheet 'NonExistentSheet' not found" in data["detail"]

def test_get_headers_no_auth(client):
    """測試無認證時獲取表頭"""
    response = client.get(
        "/api/excel/headers",
        params={"file": "test.xlsx"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
