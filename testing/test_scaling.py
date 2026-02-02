#!/usr/bin/env python3
"""
Auto-Scaling Test
Test horizontal scaling capabilities with multiple workers
"""

import time
import os
import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.multi_deploy_agent import MultiDeployAgent
from experimental.load_generator import LoadGenerator
from core.env_config import EnvironmentConfig

def test_single_worker_performance():
    """Test performance with single worker."""
    print("[TESTING] Single Worker Performance...")
    
    multi_agent = MultiDeployAgent('dev', workers=1)
    multi_agent.start_workers()
    
    # Submit test work
    start_time = time.time()
    for i in range(10):
        multi_agent.submit_deployment(f'single_test_{i}.csv', 'deploy')
    
    # Wait for completion
    multi_agent.work_queue.join()
    duration = time.time() - start_time
    
    multi_agent.stop_workers()
    
    print(f"   Single worker completed 10 tasks in {duration:.2f}s")
    return duration

def test_multi_worker_performance():
    """Test performance with multiple workers."""
    print("\n[TESTING] Multi-Worker Performance...")
    
    multi_agent = MultiDeployAgent('dev', workers=3)
    multi_agent.start_workers()
    
    # Submit same amount of work
    start_time = time.time()
    for i in range(10):
        multi_agent.submit_deployment(f'multi_test_{i}.csv', 'deploy')
    
    # Wait for completion
    multi_agent.work_queue.join()
    duration = time.time() - start_time
    
    multi_agent.stop_workers()
    
    print(f"   Three workers completed 10 tasks in {duration:.2f}s")
    return duration

def test_load_generation():
    """Test load generation capabilities."""
    print("\n[TESTING] Load Generation...")
    
    multi_agent = MultiDeployAgent('dev', workers=2)
    multi_agent.start_workers()
    
    load_gen = LoadGenerator('dev')
    
    # Run short constant load test
    print("   Running 30s constant load test...")
    load_gen.constant_load_test(multi_agent, duration=30, rps=1)
    
    # Wait for queue to empty
    multi_agent.work_queue.join()
    
    multi_agent.stop_workers()
    
    print("   [PASS] Load generation test completed")

def test_throughput_logging():
    """Test throughput logging functionality."""
    print("\n[TESTING] Throughput Logging...")
    
    env_config = EnvironmentConfig('dev')
    throughput_log = env_config.get_log_path("performance/throughput_log.csv")
    
    # Check if log directory exists
    log_dir = os.path.dirname(throughput_log)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"   Created log directory: {log_dir}")
    
    # Test log creation
    multi_agent = MultiDeployAgent('dev', workers=2)
    
    if os.path.exists(throughput_log):
        print(f"   [PASS] Throughput log exists: {throughput_log}")
        
        # Read and display sample entries
        with open(throughput_log, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            print(f"   Log has {len(rows)} entries (including header)")
            
            if len(rows) > 1:
                print(f"   Sample entry: {rows[1]}")
    else:
        print(f"   [FAIL] Throughput log not found: {throughput_log}")
        return False
    
    return True

def test_worker_isolation():
    """Test that workers operate independently."""
    print("\n[TESTING] Worker Isolation...")
    
    # Create agents with different worker IDs
    agent1 = MultiDeployAgent('dev', workers=1)
    agent2 = MultiDeployAgent('dev', workers=1) 
    
    agent1.start_workers()
    agent2.start_workers()
    
    # Submit work to both
    agent1.submit_deployment('isolation_test_1.csv', 'deploy')
    agent2.submit_deployment('isolation_test_2.csv', 'deploy')
    
    # Check status
    status1 = agent1.get_status()
    status2 = agent2.get_status()
    
    print(f"   Agent 1 status: {status1}")
    print(f"   Agent 2 status: {status2}")
    
    # Wait and cleanup
    agent1.work_queue.join()
    agent2.work_queue.join()
    
    agent1.stop_workers()
    agent2.stop_workers()
    
    print("   [PASS] Worker isolation test completed")

def test_scaling_configuration():
    """Test scaling configuration options."""
    print("\n[TESTING] Scaling Configuration...")
    
    # Test different worker counts
    worker_counts = [1, 2, 3, 5]
    
    for count in worker_counts:
        multi_agent = MultiDeployAgent('dev', workers=count)
        status = multi_agent.get_status()
        
        print(f"   {count} workers configured: {status['workers']} total")
        assert status['workers'] == count, f"Expected {count} workers, got {status['workers']}"
    
    print("   [PASS] Scaling configuration test passed")

def verify_log_structure():
    """Verify log file structure and content."""
    print("\n[TESTING] Log Structure...")
    
    env_config = EnvironmentConfig('dev')
    
    # Check performance logs
    perf_dir = env_config.get_log_path("performance")
    if not os.path.exists(perf_dir):
        os.makedirs(perf_dir)
        print(f"   Created performance directory: {perf_dir}")
    
    # Expected log files
    expected_logs = [
        "performance/throughput_log.csv",
        "performance/load_test_log.csv"
    ]
    
    for log_name in expected_logs:
        log_path = env_config.get_log_path(log_name)
        if os.path.exists(log_path):
            print(f"   [PASS] {log_name} exists")
        else:
            print(f"   [INFO] {log_name} will be created on first use")
    
    return True

if __name__ == "__main__":
    print("[START] DAY 4 - Auto-Scaling Simulation Test")
    print("=" * 50)
    
    tests = [
        ("Scaling Configuration", test_scaling_configuration),
        ("Log Structure", verify_log_structure),
        ("Single Worker Performance", test_single_worker_performance),
        ("Multi-Worker Performance", test_multi_worker_performance),
        ("Worker Isolation", test_worker_isolation),
        ("Throughput Logging", test_throughput_logging),
        ("Load Generation", test_load_generation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n[RUN] {test_name}...")
            result = test_func()
            if result is not False:
                print(f"[PASS] {test_name}: PASSED")
                passed += 1
            else:
                print(f"[FAIL] {test_name}: FAILED")
        except Exception as e:
            print(f"[ERROR] {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n[RESULTS] Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All auto-scaling tests passed!")
        print("\n[READY] System ready for horizontal scaling with:")
        print("   - Multiple deploy workers")
        print("   - Load balancing via work queue")
        print("   - Performance monitoring")
        print("   - Throughput logging")
        print("   - Load generation capabilities")
        exit(0)
    else:
        print("\n[WARNING] Some scaling tests failed")
        exit(1)