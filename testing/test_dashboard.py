#!/usr/bin/env python3
"""Test dashboard functionality."""

import pandas as pd
import os

def test_dashboard_data():
    """Test if dashboard can load required data files."""
    
    print("🧪 Testing Dashboard Data Loading...")
    
    required_files = [
        os.path.join("logs", r"deployment_log.csv"),
        os.path.join("logs", r"healing_log.csv"), 
        os.path.join("logs", r"issue_log.csv"),
        os.path.join("logs", r"uptime_log.csv")
    ]
    
    results = {}
    
    for file_path in required_files:
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                results[file_path] = {
                    'status': '✅ OK',
                    'rows': len(df),
                    'columns': list(df.columns)
                }
            except Exception as e:
                results[file_path] = {
                    'status': f'❌ Error: {str(e)}',
                    'rows': 0,
                    'columns': []
                }
        else:
            results[file_path] = {
                'status': '⚠️ Missing',
                'rows': 0,
                'columns': []
            }
    
    # Print results
    print("\n📊 Data File Status:")
    for file_path, info in results.items():
        print(f"{info['status']} {file_path} ({info['rows']} rows)")
        if info['columns']:
            print(f"   Columns: {', '.join(info['columns'][:5])}{'...' if len(info['columns']) > 5 else ''}")
    
    # Check if dashboard can run
    working_files = sum(1 for info in results.values() if '✅' in info['status'])
    total_files = len(required_files)
    
    print(f"\n🎯 Dashboard Readiness: {working_files}/{total_files} files OK")
    
    if working_files >= 2:
        print("🟢 Dashboard should work with available data")
        return True
    else:
        print("🔴 Dashboard may have limited functionality")
        return False

def create_sample_data():
    """Create minimal sample data if files are missing."""
    
    print("\n🔧 Creating sample data...")
    
    # Sample deployment log
    if not os.path.exists(os.path.join("logs", r"deployment_log.csv")):
        sample_deploy = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=5, freq='H'),
            'status': ['success', 'success', 'failure', 'success', 'success'],
            'details': ['Deploy v1.0', 'Deploy v1.1', 'Deploy v1.2 failed', 'Deploy v1.3', 'Deploy v1.4']
        })
        sample_deploy.to_csv(os.path.join("logs", r"deployment_log.csv"), index=False)
        print("✅ Created sample deployment_log.csv")
    
    # Sample healing log
    if not os.path.exists(os.path.join("logs", r"healing_log.csv")):
        sample_heal = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01 02:00', periods=3, freq='2H'),
            'strategy': ['retry', 'restore', 'adjust'],
            'status': ['success', 'failure', 'success']
        })
        sample_heal.to_csv(os.path.join("logs", r"healing_log.csv"), index=False)
        print("✅ Created sample healing_log.csv")
    
    # Sample issue log
    if not os.path.exists(os.path.join("logs", r"issue_log.csv")):
        sample_issues = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01 01:30', periods=2, freq='3H'),
            'failure_state': ['deployment_failure', 'latency_issue'],
            'reason': ['Build failed', 'High response time']
        })
        sample_issues.to_csv(os.path.join("logs", r"issue_log.csv"), index=False)
        print("✅ Created sample issue_log.csv")
    
    # Sample uptime log
    if not os.path.exists(os.path.join("logs", r"uptime_log.csv")):
        sample_uptime = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=10, freq='30min'),
            'status': ['UP'] * 8 + ['DOWN', 'UP']
        })
        sample_uptime.to_csv(os.path.join("logs", r"uptime_log.csv"), index=False)
        print("✅ Created sample uptime_log.csv")

if __name__ == "__main__":
    # Test current data
    dashboard_ready = test_dashboard_data()
    
    if not dashboard_ready:
        create_sample_data()
        print("\n🔄 Re-testing after creating sample data...")
        test_dashboard_data()
    
    print("\n🚀 Dashboard test complete!")
    print("💡 Run: python run_web_dashboard.py")
    print("🌐 Or: streamlit run web_dashboard.py")