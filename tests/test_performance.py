"""
效能測試
"""
import pytest
import time

@pytest.mark.slow
class TestPerformance:
    """效能測試類別"""
    
    def test_append_performance(self, client, auth_headers):
        """測試新增操作效能"""
        NUM_OPERATIONS = 100
        
        start_time = time.time()
        for i in range(NUM_OPERATIONS):
            response = client.post(
                "/api/excel/append",
                headers=auth_headers,
                json={
                    "file": "perf_test.xlsx",
                    "sheet": "Sheet1",
                    "values": [f"ID{i:04d}", f"User {i}", "Dept", 50000 + i]
                }
            )
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        avg_time = elapsed / NUM_OPERATIONS
        
        print(f"\n{NUM_OPERATIONS} append operations:")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average time per operation: {avg_time*1000:.2f}ms")
        print(f"Throughput: {NUM_OPERATIONS/elapsed:.2f} ops/sec")
        
        # 驗證每次操作平均不超過 200ms
        assert avg_time < 0.2, f"Average time {avg_time:.3f}s exceeds 200ms threshold"
    
    def test_read_performance(self, client, auth_headers):
        """測試讀取操作效能"""
        # 先建立測試資料
        for i in range(1000):
            client.post(
                "/api/excel/append",
                headers=auth_headers,
                json={
                    "file": "read_perf_test.xlsx",
                    "sheet": "Sheet1",
                    "values": [f"ID{i:04d}", f"User {i}", "Dept", 50000]
                }
            )
        
        # 測試讀取效能
        NUM_READS = 50
        start_time = time.time()
        
        for _ in range(NUM_READS):
            response = client.post(
                "/api/excel/read",
                headers=auth_headers,
                json={
                    "file": "read_perf_test.xlsx",
                    "sheet": "Sheet1"
                }
            )
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        avg_time = elapsed / NUM_READS
        
        print(f"\n{NUM_READS} read operations (1000 rows):")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average time per operation: {avg_time*1000:.2f}ms")
        print(f"Throughput: {NUM_READS/elapsed:.2f} ops/sec")
        
        # 驗證讀取操作足夠快
        assert avg_time < 0.1, f"Average read time {avg_time:.3f}s exceeds 100ms threshold"
    
    def test_batch_performance(self, client, auth_headers):
        """測試批次操作效能"""
        BATCH_SIZE = 50
        
        operations = []
        for i in range(BATCH_SIZE):
            operations.append({
                "type": "append",
                "values": [f"B{i:04d}", f"Batch User {i}", "Dept", 50000]
            })
        
        start_time = time.time()
        response = client.post(
            "/api/excel/batch",
            headers=auth_headers,
            json={
                "file": "batch_perf_test.xlsx",
                "sheet": "Sheet1",
                "operations": operations
            }
        )
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == BATCH_SIZE
        
        print(f"\nBatch operation ({BATCH_SIZE} operations):")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average time per operation: {elapsed/BATCH_SIZE*1000:.2f}ms")
        
        # 批次操作應該比單獨操作更快
        assert elapsed < BATCH_SIZE * 0.05, "Batch operation not efficient enough"
    
    def test_update_performance(self, client, auth_headers):
        """測試更新操作效能"""
        # 先建立測試資料
        NUM_ROWS = 100
        for i in range(NUM_ROWS):
            client.post(
                "/api/excel/append",
                headers=auth_headers,
                json={
                    "file": "update_perf_test.xlsx",
                    "sheet": "Sheet1",
                    "values": [f"ID{i:04d}", f"User {i}", "Dept", 50000]
                }
            )
        
        # 測試更新效能
        NUM_UPDATES = 50
        start_time = time.time()
        
        for i in range(NUM_UPDATES):
            row_num = (i % NUM_ROWS) + 1  # 循環更新不同的列
            response = client.put(
                "/api/excel/update",
                headers=auth_headers,
                json={
                    "file": "update_perf_test.xlsx",
                    "sheet": "Sheet1",
                    "row": row_num,
                    "values": [f"UPD{i:04d}", f"Updated {i}", "Updated", 99999],
                    "column_start": 1
                }
            )
            assert response.status_code == 200
        
        elapsed = time.time() - start_time
        avg_time = elapsed / NUM_UPDATES
        
        print(f"\n{NUM_UPDATES} update operations:")
        print(f"Total time: {elapsed:.2f}s")
        print(f"Average time per operation: {avg_time*1000:.2f}ms")
        print(f"Throughput: {NUM_UPDATES/elapsed:.2f} ops/sec")
        
        # 驗證更新操作效能
        assert avg_time < 0.15, f"Average update time {avg_time:.3f}s exceeds 150ms threshold"
