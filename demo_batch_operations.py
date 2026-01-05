"""
演示批量更新和批量刪除功能
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_TOKEN = "your-secret-token-here"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def demo_batch_update():
    """演示批量更新功能"""
    print("\n=== 批量更新演示 ===")
    
    # 1. 創建測試檔案並新增資料
    print("\n1. 新增測試資料...")
    test_data = [
        ["E001", "Alice", "Engineering", 70000],
        ["E002", "Bob", "Engineering", 75000],
        ["E003", "Charlie", "Engineering", 72000],
        ["E004", "David", "Sales", 65000],
        ["E005", "Eve", "Sales", 68000],
    ]
    
    for data in test_data:
        response = requests.post(
            f"{BASE_URL}/api/excel/append",
            headers=HEADERS,
            json={
                "file": "demo_batch.xlsx",
                "sheet": "Sheet1",
                "values": data
            }
        )
        print(f"  新增: {data[1]} ({data[2]}) - {response.json()}")
    
    # 2. 批量更新所有 Engineering 部門的薪資
    print("\n2. 批量更新所有 Engineering 部門員工薪資為 85000...")
    response = requests.put(
        f"{BASE_URL}/api/excel/update_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "Engineering",
            "values_to_set": {
                "Salary": 85000
            }
        }
    )
    result = response.json()
    print(f"  結果: {json.dumps(result, indent=2)}")
    print(f"  ✓ 成功更新 {result['updated_count']} 筆記錄")
    
    # 3. 讀取資料驗證
    print("\n3. 讀取資料驗證...")
    response = requests.post(
        f"{BASE_URL}/api/excel/read",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1"
        }
    )
    data = response.json()["data"]
    print("  當前資料:")
    for row in data:
        print(f"    {row}")

def demo_batch_delete():
    """演示批量刪除功能"""
    print("\n\n=== 批量刪除演示 ===")
    
    # 1. 批量刪除所有 Sales 部門的記錄
    print("\n1. 批量刪除所有 Sales 部門員工...")
    response = requests.request(
        "DELETE",
        f"{BASE_URL}/api/excel/delete_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "Sales"
        }
    )
    result = response.json()
    print(f"  結果: {json.dumps(result, indent=2)}")
    print(f"  ✓ 成功刪除 {result['deleted_count']} 筆記錄")
    
    # 2. 讀取資料驗證
    print("\n2. 讀取資料驗證...")
    response = requests.post(
        f"{BASE_URL}/api/excel/read",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1"
        }
    )
    data = response.json()["data"]
    print("  剩餘資料:")
    for row in data:
        print(f"    {row}")
    print(f"\n  ✓ 只剩下 {len(data)-1} 筆資料記錄 (不含標題列)")

if __name__ == "__main__":
    print("=" * 60)
    print("批量操作功能演示")
    print("=" * 60)
    print("\n請確保 Excel API Server 正在運行 (http://localhost:8000)")
    print("如果需要，請先執行: python main.py")
    
    try:
        demo_batch_update()
        demo_batch_delete()
        print("\n" + "=" * 60)
        print("✓ 演示完成！")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n✗ 錯誤: 無法連接到 API Server")
        print("  請先啟動服務器: python main.py")
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
