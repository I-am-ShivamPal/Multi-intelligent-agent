#!/usr/bin/env python3
"""Test QA Metrics Dashboard functionality"""
import os
import pandas as pd
from datetime import datetime, timedelta
from dashboard.qa_metrics_tab import load_qa_data, calculate_qa_metrics, export_daily_summary

def create_sample_qa_data():
    """Create sample data for QA metrics testing"""
    os.makedirs('logs', exist_ok=True)
    
    # Sample infrastructure health data
    infra_data = []
    base_time = datetime.now() - timedelta(hours=24)
    for i in range(144):  # 24 hours of 10-minute intervals
        timestamp = base_time + timedelta(minutes=i*10)
        healthy = True if i % 20 != 0 else False  # 95% uptime
        infra_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'container_name': 'cicd-dashboard',
            'status': 'Up 2 hours' if healthy else 'Restarting',
            'healthy': healthy
        })
    
    pd.DataFrame(infra_data).to_csv('logs/infra_health.csv', index=False)
    
    # Sample healing data
    healing_data = []
    for i in range(10):
        timestamp = base_time + timedelta(hours=i*2)
        healing_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'strategy': ['retry', 'restore', 'adjust'][i % 3],
            'status': 'success' if i % 4 != 0 else 'failure'
        })
    
    pd.DataFrame(healing_data).to_csv('logs/healing_log.csv', index=False)
    
    # Sample issue data
    issue_data = []
    for i in range(5):
        timestamp = base_time + timedelta(hours=i*4)
        issue_data.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'failure_state': ['deployment_failure', 'latency_issue'][i % 2],
            'severity': 'high'
        })
    
    pd.DataFrame(issue_data).to_csv('logs/issue_log.csv', index=False)

def test_qa_metrics():
    """Test QA metrics calculation and export"""
    print("=== DAY 3 QA METRICS TEST ===\n")
    
    # Create sample data
    print("✓ Creating sample QA data...")
    create_sample_qa_data()
    
    # Load data
    print("✓ Loading QA data...")
    data = load_qa_data()
    
    # Calculate metrics
    print("✓ Calculating QA metrics...")
    metrics = calculate_qa_metrics(data)
    
    # Display results
    print(f"\n📊 QA METRICS RESULTS:")
    print(f"  Uptime %: {metrics['uptime_pct']:.1f}%")
    print(f"  Avg Recovery Time: {metrics['avg_recovery_time']:.1f} min")
    print(f"  Error Frequency: {metrics['error_frequency']:.2f}/hr")
    print(f"  Fix Success %: {metrics['fix_success_pct']:.1f}%")
    
    # Export daily summary
    print("\n✓ Exporting daily summary...")
    filename, summary_df = export_daily_summary(data, metrics)
    print(f"  Exported: {filename}")
    print(f"  Summary:\n{summary_df.to_string(index=False)}")
    
    # Verify files
    files_created = [
        'logs/infra_health.csv',
        'logs/healing_log.csv', 
        'logs/issue_log.csv',
        filename
    ]
    
    all_exist = all(os.path.exists(f) for f in files_created)
    
    print(f"\n✓ Files created: {len([f for f in files_created if os.path.exists(f)])}/{len(files_created)}")
    
    success = all_exist and metrics['uptime_pct'] > 0
    print(f"\nStatus: {'🟢 PASSED' if success else '🔴 FAILED'}")
    
    return success

if __name__ == '__main__':
    success = test_qa_metrics()
    
    if success:
        print("\nDAY 3 QA METRICS:")
        print("✓ QA metrics calculation")
        print("✓ Telemetry data processing")
        print("✓ Automated daily reporting")
        print("✓ System stability monitoring")