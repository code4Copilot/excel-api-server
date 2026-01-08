"""
CRUD 操作測試
"""
import pytest
from fastapi import status

class TestAppendOperations:
    """新增操作測試"""
    
    def test_append_to_new_file(self, client, auth_headers):
        """測試新增到新檔案"""
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": "new_file.xlsx",
                "sheet": "Sheet1",
                "values": ["E001", "Test User", "IT", 50000]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["row_number"] >= 1
    
    def test_append_to_existing_file(self, client, auth_headers, sample_excel_file):
        """測試新增到現有檔案"""
        response = client.post(
            "/api/excel/append",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "values": ["E004", "New Employee", "Marketing", 70000]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["row_number"] == 5  # 1 header + 3 existing + 1 new
    
    def test_append_object_mode(self, client, auth_headers, sample_excel_file):
        """測試物件模式新增"""
        response = client.post(
            "/api/excel/append_object",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "values": {
                    "ID": "E005",
                    "Name": "Object User",
                    "Department": "Finance",
                    "Salary": 80000
                }
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["matched_columns"]) == 4
        assert len(data["ignored_columns"]) == 0

class TestReadOperations:
    """讀取操作測試"""
    
    def test_read_all_data(self, client, auth_headers, sample_excel_file):
        """測試讀取所有資料"""
        response = client.post(
            "/api/excel/read",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["row_count"] == 4  # 1 header + 3 data rows
        assert data["data"][0] == ["ID", "Name", "Department", "Salary"]
    
    def test_read_specific_range(self, client, auth_headers, sample_excel_file):
        """測試讀取特定範圍"""
        response = client.post(
            "/api/excel/read",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "range": "A1:B3"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert len(data["data"][0]) == 2  # Only 2 columns
    
    def test_read_nonexistent_file(self, client, auth_headers):
        """測試讀取不存在的檔案"""
        response = client.post(
            "/api/excel/read",
            headers=auth_headers,
            json={
                "file": "nonexistent.xlsx",
                "sheet": "Sheet1"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_read_nonexistent_sheet(self, client, auth_headers, sample_excel_file):
        """測試讀取不存在的工作表"""
        response = client.post(
            "/api/excel/read",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "NonExistentSheet"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Sheet 'NonExistentSheet' not found" in data["detail"]

class TestUpdateOperations:
    """更新操作測試"""
    
    def test_update_by_row_number(self, client, auth_headers, sample_excel_file):
        """測試按列號更新"""
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "row": 2,
                "values_to_set": {
                    "Name": "Updated Name",
                    "Department": "Updated Dept",
                    "Salary": 99000
                }
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] == 1
    
    def test_update_advanced_by_lookup(self, client, auth_headers, sample_excel_file):
        """測試進階更新（Lookup 模式）"""
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "ID",
                "lookup_value": "E002",
                "values_to_set": {
                    "Name": "Updated Jane",
                    "Salary": 75000
                }
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] == 1
        assert 3 in data["rows_updated"]
    
    def test_update_advanced_multiple_matches(self, client, auth_headers, sample_excel_file):
        """測試進階更新（多筆符合條件 - process_all=True）"""
        # 先新增兩筆相同 Department 的記錄
        client.post("/api/excel/append", headers=auth_headers, 
                   json={"file": "test.xlsx", "sheet": "Sheet1", 
                         "values": ["E004", "User4", "Engineering", 60000]})
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E005", "User5", "Engineering", 65000]})
        
        # 更新所有 Engineering 部門的 Salary（預設 process_all=True）
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "Department",
                "lookup_value": "Engineering",
                "process_all": True,
                "values_to_set": {
                    "Salary": 80000
                }
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] == 3  # E001 + E004 + E005
        assert len(data["rows_updated"]) == 3
        assert data["process_mode"] == "all"
    
    def test_update_advanced_first_match_only(self, client, auth_headers, sample_excel_file):
        """測試進階更新（只處理第一筆 - process_all=False）"""
        # 先新增兩筆相同 Department 的記錄
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E004", "User4", "HR", 50000]})
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E005", "User5", "HR", 52000]})
        
        # 只更新第一筆 HR 部門的記錄
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "Department",
                "lookup_value": "HR",
                "process_all": False,
                "values_to_set": {
                    "Salary": 90000
                }
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["updated_count"] == 1  # 只處理第一筆
        assert len(data["rows_updated"]) == 1
        assert data["process_mode"] == "first"
    
    def test_update_invalid_row(self, client, auth_headers, sample_excel_file):
        """測試更新無效列號"""
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "row": 999,
                "values_to_set": {
                    "Name": "Test"
                }
            }
        )
        # 超出範圍的列號會引發 400 錯誤
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_update_nonexistent_sheet(self, client, auth_headers, sample_excel_file):
        """測試更新不存在的工作表"""
        response = client.put(
            "/api/excel/update_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "NonExistentSheet",
                "row": 2,
                "values_to_set": {
                    "Name": "Test"
                }
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Sheet 'NonExistentSheet' not found" in data["detail"]

class TestDeleteOperations:
    """刪除操作測試"""
    
    def test_delete_by_row_number(self, client, auth_headers, sample_excel_file):
        """測試按列號刪除"""
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "row": 2
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 1
    
    def test_delete_advanced_by_lookup(self, client, auth_headers, sample_excel_file):
        """測試進階刪除（Lookup 模式）"""
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "ID",
                "lookup_value": "E003"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 1
        assert 4 in data["rows_deleted"]
    
    def test_delete_advanced_multiple_matches(self, client, auth_headers, sample_excel_file):
        """測試進階刪除（多筆符合條件 - process_all=True）"""
        # 先新增兩筆相同 Department 的記錄
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E004", "User4", "Sales", 55000]})
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E005", "User5", "Sales", 58000]})
        
        # 刪除所有 Sales 部門的記錄（預設 process_all=True）
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "Department",
                "lookup_value": "Sales",
                "process_all": True
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 3  # E002 + E004 + E005
        assert len(data["rows_deleted"]) == 3
        assert data["process_mode"] == "all"
    
    def test_delete_advanced_first_match_only(self, client, auth_headers, sample_excel_file):
        """測試進階刪除（只處理第一筆 - process_all=False）"""
        # 先新增兩筆相同 Department 的記錄
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E004", "User4", "Marketing", 45000]})
        client.post("/api/excel/append", headers=auth_headers,
                   json={"file": "test.xlsx", "sheet": "Sheet1",
                         "values": ["E005", "User5", "Marketing", 48000]})
        
        # 只刪除第一筆 Marketing 部門的記錄
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "Department",
                "lookup_value": "Marketing",
                "process_all": False
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
        assert data["deleted_count"] == 1  # 只處理第一筆
        assert len(data["rows_deleted"]) == 1
        assert data["process_mode"] == "first"
    
    def test_delete_nonexistent_row(self, client, auth_headers, sample_excel_file):
        """測試刪除不存在的列"""
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "Sheet1",
                "lookup_column": "ID",
                "lookup_value": "E999"
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_nonexistent_sheet(self, client, auth_headers, sample_excel_file):
        """測試刪除不存在的工作表"""
        response = client.request(
            "DELETE",
            "/api/excel/delete_advanced",
            headers=auth_headers,
            json={
                "file": "test.xlsx",
                "sheet": "NonExistentSheet",
                "row": 2
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        data = response.json()
        assert "Sheet 'NonExistentSheet' not found" in data["detail"]
