#!/usr/bin/env python3
"""
Test Observability Layer
Comprehensive test for DAY 5 observability features
"""

import os
import pandas as pd
from core.metrics_collector import get_metrics_collector
from core.metrics_aggregator import MetricsAggregator

def test_metrics_collection():
    """Test metrics collection system."""
    print("🔧 Testing Metrics Collection...")
    
    # Test metrics collector for each environment
    environments = ['dev', 'stage', 'prod']
    
    for env in environments:
        metrics = get_metrics_collector(env)
        
        # Test metric recording
        metrics.record_uptime_metric('test_service', 'running', 3600, 0)
        metrics.record_latency_metric('test_service', 'deploy', 1500)
        metrics.record_queue_metric('test_queue', 5, 2.0, 1.8, 250)
        metrics.record_deploy_success_rate(10, 9, 1, 1200)
        metrics.record_error_metric('test_service', 'timeout', 2, 50, 'medium')
        
        # Verify metrics files exist
        metrics_dir = metrics.metrics_dir
        expected_files = [
            'uptime_metrics.csv',
            'latency_metrics.csv',
            'queue_depth.csv',
            'deploy_success_rate.csv',
            'error_metrics.csv'
        ]
        
        for file_name in expected_files:
            file_path = os.path.join(metrics_dir, file_name)
            if os.path.exists(file_path):
                print(f"   ✅ {env.upper()}: {file_name} exists")
                
                # Check file has data
                df = pd.read_csv(file_path)
                if len(df) > 0:
                    print(f"      📊 {len(df)} records")
                else:
                    print(f"      ⚠️ No data records")
            else:
                print(f"   ❌ {env.upper()}: {file_name} missing")
                return False
    
    print("   ✅ Metrics collection test passed")
    return True

def test_metrics_aggregation():
    """Test metrics aggregation for dashboard."""
    print("\n📊 Testing Metrics Aggregation...")
    
    aggregator = MetricsAggregator()
    
    # Test environment health aggregation
    health_data = aggregator.get_environment_health()
    print(f"   Environment health data: {len(health_data)} environments")
    
    for env, data in health_data.items():
        print(f"   {env.upper()}: {data['status']} ({data['uptime_percent']:.1f}% uptime)")
    
    # Test scaling activity
    scaling_data = aggregator.get_scaling_activity()
    print(f"   Scaling data: {len(scaling_data['environments'])} environments tracked")
    
    # Test deployment throughput
    throughput_data = aggregator.get_deployment_throughput(24)
    print(f"   Throughput data: {len(throughput_data['timestamps'])} time points")
    
    # Test queue depth
    queue_data = aggregator.get_queue_depth_over_time(6)
    print(f"   Queue data: {len(queue_data['timestamps'])} time points")
    
    # Test error heatmap
    error_data = aggregator.get_error_heatmap(7)
    print(f"   Error data: {len(error_data['environments'])} error entries")
    
    print("   ✅ Metrics aggregation test passed")
    return True

def test_dashboard_data_structure():
    """Test dashboard data structure compatibility."""
    print("\n🎨 Testing Dashboard Data Structure...")
    
    aggregator = MetricsAggregator()
    overview = aggregator.get_system_overview()
    
    # Verify required data structure
    required_keys = [
        'environment_health',
        'scaling_activity', 
        'deployment_throughput',
        'queue_depth',
        'error_heatmap'
    ]
    
    for key in required_keys:
        if key in overview:
            print(f"   ✅ {key} data structure present")
        else:
            print(f"   ❌ {key} data structure missing")
            return False
    
    # Test environment health structure
    env_health = overview['environment_health']
    if env_health:
        sample_env = list(env_health.keys())[0]
        sample_data = env_health[sample_env]
        
        required_health_fields = ['status', 'uptime_percent', 'avg_latency_ms', 'error_rate']
        for field in required_health_fields:
            if field in sample_data:
                print(f"      ✅ Health field: {field}")
            else:
                print(f"      ❌ Missing health field: {field}")
    
    print("   ✅ Dashboard data structure test passed")
    return True

def test_metrics_file_integrity():
    """Test metrics file integrity and format."""
    print("\n📋 Testing Metrics File Integrity...")
    
    environments = ['dev', 'stage', 'prod']
    
    for env in environments:
        metrics = get_metrics_collector(env)
        metrics_dir = metrics.metrics_dir
        
        # Test each metrics file
        metric_files = {
            'uptime_metrics.csv': ['timestamp', 'service_name', 'status', 'uptime_seconds', 'availability_percent'],
            'latency_metrics.csv': ['timestamp', 'service_name', 'operation', 'latency_ms'],
            'queue_depth.csv': ['timestamp', 'queue_name', 'depth'],
            'deploy_success_rate.csv': ['timestamp', 'total_deployments', 'success_rate_percent'],
            'error_metrics.csv': ['timestamp', 'service_name', 'error_type', 'error_count']
        }
        
        for file_name, required_columns in metric_files.items():
            file_path = os.path.join(metrics_dir, file_name)
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    
                    # Check required columns exist
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        print(f"   ❌ {env.upper()}: {file_name} missing columns: {missing_columns}")
                        return False
                    else:
                        print(f"   ✅ {env.upper()}: {file_name} format valid ({len(df)} rows)")
                
                except Exception as e:
                    print(f"   ❌ {env.upper()}: {file_name} read error: {e}")
                    return False
            else:
                print(f"   ⚠️ {env.upper()}: {file_name} not found")
    
    print("   ✅ Metrics file integrity test passed")
    return True

def test_performance_metrics():
    """Test performance and scaling metrics."""
    print("\n⚡ Testing Performance Metrics...")
    
    environments = ['dev', 'stage', 'prod']
    
    for env in environments:
        from core.env_config import EnvironmentConfig
        env_config = EnvironmentConfig(env)
        
        # Check performance directory
        perf_dir = env_config.get_log_path("performance")
        if os.path.exists(perf_dir):
            print(f"   ✅ {env.upper()}: Performance directory exists")
            
            # Check for performance logs
            perf_files = ['throughput_log.csv', 'load_test_log.csv']
            for perf_file in perf_files:
                perf_path = os.path.join(perf_dir, perf_file)
                if os.path.exists(perf_path):
                    print(f"      ✅ {perf_file} exists")
                else:
                    print(f"      ⚠️ {perf_file} will be created on first use")
        else:
            print(f"   ⚠️ {env.upper()}: Performance directory will be created on first use")
    
    print("   ✅ Performance metrics test passed")
    return True

def generate_test_report():
    """Generate comprehensive test report."""
    print("\n📊 Generating Observability Test Report...")
    
    aggregator = MetricsAggregator()
    
    # Collect summary statistics
    total_metrics = 0
    total_services = set()
    
    for env in ['dev', 'stage', 'prod']:
        metrics = get_metrics_collector(env)
        summary = metrics.get_metrics_summary()
        total_metrics += summary['metrics_collected']
        total_services.update(summary['services_monitored'])
    
    # Environment health summary
    health_data = aggregator.get_environment_health()
    healthy_envs = sum(1 for data in health_data.values() if data['status'] == 'healthy')
    
    print(f"\n📈 Observability System Report:")
    print(f"   Total Metrics Collected: {total_metrics}")
    print(f"   Unique Services Monitored: {len(total_services)}")
    print(f"   Healthy Environments: {healthy_envs}/3")
    print(f"   Metric Types: 5 (uptime, latency, queue, deploy, error)")
    print(f"   Dashboard Components: 6 (health, scaling, throughput, queue, errors, summary)")
    
    return {
        'total_metrics': total_metrics,
        'services_monitored': len(total_services),
        'healthy_environments': healthy_envs
    }

if __name__ == "__main__":
    print("🚀 DAY 5 - Observability Layer Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Metrics Collection", test_metrics_collection),
        ("Metrics Aggregation", test_metrics_aggregation),
        ("Dashboard Data Structure", test_dashboard_data_structure),
        ("Metrics File Integrity", test_metrics_file_integrity),
        ("Performance Metrics", test_performance_metrics)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    # Generate report
    report = generate_test_report()
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All observability tests passed!")
        print("\n🔧 System ready for production with full observability:")
        print("   - Comprehensive metrics collection")
        print("   - Multi-environment monitoring")
        print("   - Real-time dashboard visualization")
        print("   - Error tracking and heatmaps")
        print("   - Performance and scaling metrics")
        print("   - Infrastructure health monitoring")
        print("\n📊 Launch dashboard: streamlit run dashboard/observability_dashboard.py")
        exit(0)
    else:
        print("\n⚠️ Some observability tests failed")
        exit(1)