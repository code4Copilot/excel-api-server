"""
演示批量更新和批量刪除功能（包含 v3.4.0 新增的 process_all 參數）
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
API_TOKEN = os.getenv("API_TOKEN", "your-secret-token-here")
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

def print_section(title):
    """列印區塊標題"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def create_test_data():
    """創建測試資料"""
    print_section("步驟 1：創建測試資料")
    
    # 先新增標題列
    print("新增標題列...")
    response = requests.post(
        f"{BASE_URL}/api/excel/append",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "values": ["ID", "Name", "Department", "Salary"]
        }
    )
    print(f"  ✓ 標題列: {response.json()}")
    
    # 新增測試資料
    test_data = [
        ["E001", "Alice", "Engineering", 70000],
        ["E002", "Bob", "Engineering", 75000],
        ["E003", "Charlie", "Engineering", 72000],
        ["E004", "David", "Sales", 65000],
        ["E005", "Eve", "Sales", 68000],
        ["E006", "Frank", "Sales", 67000],
        ["E007", "Grace", "HR", 60000],
        ["E008", "Henry", "HR", 62000],
    ]
    
    print("\n新增員工資料...")
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
        print(f"  ✓ {data[1]:10} ({data[2]:12}) - 薪資: ${data[3]:,}")
    
    print(f"\n共新增 {len(test_data)} 筆員工記錄")

def read_and_display_data(title="當前資料"):
    """讀取並顯示資料"""
    print(f"\n{title}:")
    response = requests.post(
        f"{BASE_URL}/api/excel/read",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1"
        }
    )
    data = response.json()["data"]
    for i, row in enumerate(data):
        if i == 0:
            print(f"  {'列號':<6} {row[0]:<8} {row[1]:<12} {row[2]:<15} {row[3]}")
            print(f"  {'-'*60}")
        else:
            print(f"  {i+1:<6} {row[0]:<8} {row[1]:<12} {row[2]:<15} ${row[3]:,}")
    return len(data) - 1  # 不含標題列

def demo_batch_update_all():
    """演示批量更新所有符合條件的記錄 (process_all=True)"""
    print_section("步驟 2：批量更新 - 處理所有符合條件的記錄 (process_all=True)")
    
    print("\n🎯 目標: 將所有 Engineering 部門員工薪資更新為 $85,000")
    print("   使用參數: process_all=True (預設值)")
    
    response = requests.put(
        f"{BASE_URL}/api/excel/update_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "Engineering",
            "process_all": True,  # 處理所有匹配記錄
            "values_to_set": {
                "Salary": 85000
            }
        }
    )
    result = response.json()
    
    print(f"\n📊 更新結果:")
    print(f"   • 更新模式: {result['process_mode']} (處理所有匹配)")
    print(f"   • 更新記錄數: {result['updated_count']} 筆")
    print(f"   • 影響列號: {result['rows_updated']}")
    print(f"   • 更新欄位: {result['updated_columns']}")
    
    read_and_display_data("更新後的資料")

def demo_single_update():
    """演示只更新第一筆符合條件的記錄 (process_all=False)"""
    print_section("步驟 3：單筆更新 - 只處理第一筆符合條件的記錄 (process_all=False)")
    
    print("\n🎯 目標: 只將第一筆 Sales 部門員工薪資更新為 $75,000")
    print("   使用參數: process_all=False (新功能！)")
    
    response = requests.put(
        f"{BASE_URL}/api/excel/update_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "Sales",
            "process_all": False,  # 只處理第一筆
            "values_to_set": {
                "Salary": 75000
            }
        }
    )
    result = response.json()
    
    print(f"\n📊 更新結果:")
    print(f"   • 更新模式: {result['process_mode']} (只處理第一筆)")
    print(f"   • 更新記錄數: {result['updated_count']} 筆")
    print(f"   • 影響列號: {result['rows_updated']}")
    print(f"   • 更新欄位: {result['updated_columns']}")
    
    read_and_display_data("更新後的資料")

def demo_batch_delete_all():
    """演示批量刪除所有符合條件的記錄 (process_all=True)"""
    print_section("步驟 4：批量刪除 - 刪除所有符合條件的記錄 (process_all=True)")
    
    print("\n🎯 目標: 刪除所有剩餘的 Sales 部門員工")
    print("   使用參數: process_all=True (預設值)")
    
    response = requests.request(
        "DELETE",
        f"{BASE_URL}/api/excel/delete_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "Sales",
            "process_all": True  # 刪除所有匹配記錄
        }
    )
    result = response.json()
    
    print(f"\n📊 刪除結果:")
    print(f"   • 刪除模式: {result['process_mode']} (刪除所有匹配)")
    print(f"   • 刪除記錄數: {result['deleted_count']} 筆")
    print(f"   • 刪除列號: {result['rows_deleted']}")
    
    read_and_display_data("刪除後的資料")

def demo_single_delete():
    """演示只刪除第一筆符合條件的記錄 (process_all=False)"""
    print_section("步驟 5：單筆刪除 - 只刪除第一筆符合條件的記錄 (process_all=False)")
    
    print("\n🎯 目標: 只刪除第一筆 HR 部門員工")
    print("   使用參數: process_all=False (新功能！)")
    
    response = requests.request(
        "DELETE",
        f"{BASE_URL}/api/excel/delete_advanced",
        headers=HEADERS,
        json={
            "file": "demo_batch.xlsx",
            "sheet": "Sheet1",
            "lookup_column": "Department",
            "lookup_value": "HR",
            "process_all": False  # 只刪除第一筆
        }
    )
    result = response.json()
    
    print(f"\n📊 刪除結果:")
    print(f"   • 刪除模式: {result['process_mode']} (只刪除第一筆)")
    print(f"   • 刪除記錄數: {result['deleted_count']} 筆")
    print(f"   • 刪除列號: {result['rows_deleted']}")
    
    count = read_and_display_data("刪除後的資料")
    print(f"\n✓ 還有 1 筆 HR 部門員工未被刪除（因為使用 process_all=False）")


def main():
    """主函數"""
    print("=" * 70)
    print("  Excel API Server - 批次操作演示程式 v3.4.0")
    print("  功能: 展示 process_all 參數的批次處理與單筆處理模式")
    print("=" * 70)
    
    # 檢查伺服器連線
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("\n❌ 錯誤: 無法連接到 Excel API Server")
            print(f"   請確認服務是否在 {BASE_URL} 運行")
            return
        print("\n✓ 成功連接到 Excel API Server")
    except Exception as e:
        print(f"\n❌ 錯誤: 無法連接到 Excel API Server")
        print(f"   錯誤訊息: {e}")
        print(f"   請確認服務是否在 {BASE_URL} 運行")
        return
    
    try:
        # 步驟 1: 創建測試資料
        create_test_data()
        
        # 步驟 2: 批量更新所有匹配記錄 (process_all=True)
        demo_batch_update_all()
        
        # 步驟 3: 單筆更新第一筆匹配記錄 (process_all=False)
        demo_single_update()
        
        # 步驟 4: 批量刪除所有匹配記錄 (process_all=True)
        demo_batch_delete_all()
        
        # 步驟 5: 單筆刪除第一筆匹配記錄 (process_all=False)
        demo_single_delete()
        
        # 結束
        print_section("演示完成")
        print("\n🎉 所有測試成功完成！")
        print("\n📝 總結:")
        print("   • process_all=True (預設): 處理所有符合條件的記錄")
        print("   • process_all=False (新功能): 只處理第一筆符合條件的記錄")
        print("\n💡 提示: 測試檔案 'demo_batch.xlsx' 已保留在 data/ 目錄")
        
    except Exception as e:
        print(f"\n\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
