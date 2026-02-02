#!/usr/bin/env python3
"""Test MCP endpoints for cloud deployment validation."""

import requests
import json
import sys

def test_mcp_endpoints(base_url):
    """Test all MCP endpoints."""
    print(f"🧪 Testing MCP endpoints at {base_url}")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ /health endpoint working")
        else:
            print(f"❌ /health failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /health error: {e}")
    
    # Test mcp_outbox endpoint
    try:
        response = requests.get(f"{base_url}/mcp_outbox", timeout=10)
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ /mcp_outbox working ({len(messages)} messages)")
        else:
            print(f"❌ /mcp_outbox failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /mcp_outbox error: {e}")
    
    # Test mcp_inbox endpoint
    try:
        test_message = {
            "type": "test",
            "content": "Cloud deployment test",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        response = requests.post(f"{base_url}/mcp_inbox", 
                               json=test_message, timeout=10)
        if response.status_code == 200:
            print("✅ /mcp_inbox working")
        else:
            print(f"❌ /mcp_inbox failed: {response.status_code}")
    except Exception as e:
        print(f"❌ /mcp_inbox error: {e}")

def validate_main_flow():
    """Validate main.py flow components."""
    print("\n🔍 Validating main.py flow components...")
    
    required_files = [
        "main.py",
        os.path.join("agents", r"deploy_agent.py"),
        os.path.join("agents", r"issue_detector.py"), 
        os.path.join("agents", r"uptime_monitor.py"),
        os.path.join("agents", r"auto_heal_agent.py"),
        "rl/rl_trainer.py",
        "dataset/student_scores.csv"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")

if __name__ == "__main__":
    import os
    
    # Test local endpoints
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8080"
    
    test_mcp_endpoints(base_url)
    validate_main_flow()
    
    print("\n🚀 Cloud deployment validation complete!")