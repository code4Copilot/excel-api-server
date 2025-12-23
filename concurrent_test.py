"""
併發壓力測試
測試 10 個使用者同時提交資料
"""
import requests
import threading
import time
from datetime import datetime

WEBHOOK_URL = "http://localhost:5678/webhook/employee-submit"
NUM_WORKERS = 10

def submit_data(worker_id):
    """模擬一個使用者提交資料"""
    data = {
        "employeeId": f"TEST{worker_id:04d}",
        "name": f"測試員工{worker_id}",
        "department": ["技術部", "業務部", "行政部"][worker_id % 3],
        "position":["工程師","會計師", "經理", "助理"][worker_id % 4],
        "salary": 40000 + (worker_id * 1000),
        "hireDate": ["2021/10/5", "2022/5/28", "2023/8/12"][worker_id % 3],
        "status": ["在職","離職", "留職"][worker_id % 3]
    }
    
    try:
        start_time = time.time()
        response = requests.post(WEBHOOK_URL, json=data, timeout=30)
        elapsed = time.time() - start_time
        
        print(f"Worker {worker_id:2d}: Status {response.status_code} - {elapsed:.2f}s")
        return response.status_code == 200
    except Exception as e:
        print(f"Worker {worker_id:2d}: Failed - {e}")
        return False

# 同時啟動所有 Worker
print(f"開始併發測試 - {NUM_WORKERS} 個並發請求...")
start_time = time.time()

threads = []
for i in range(NUM_WORKERS):
    t = threading.Thread(target=submit_data, args=(i,))
    threads.append(t)
    t.start()

# 等待所有完成
for t in threads:
    t.join()

total_time = time.time() - start_time
print(f"\n測試完成！總耗時: {total_time:.2f}s")

# 驗證結果
print("\n驗證 Excel 檔案...")
API_URL = "http://localhost:8000"
API_TOKEN = "A9#vLz!qX7m@2hR$eT8p^Wc%yN4b*Jd"

response = requests.post(
    f"{API_URL}/api/excel/read",
    headers={"Authorization": f"Bearer {API_TOKEN}"},
    json={"file": "employees.xlsx", "sheet": "employees"}
)

if response.ok:
    data = response.json()
    row_count = data['row_count']
    print(f"Excel 檔案共有 {row_count} 列")
    
    if row_count >= NUM_WORKERS:
        print("✓ 所有資料都已成功寫入！")
    else:
        print(f"✗ 資料遺失！預期 {NUM_WORKERS} 列，實際 {row_count} 列")
else:
    print("✗ 無法讀取 Excel 檔案")
