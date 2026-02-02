#!/usr/bin/env python3
"""Test MCP bridge integration."""

import json
import requests
import time
from core.sovereign_bus import bus
from core.mcp_bridge import mcp_bridge

def test_bus_to_mcp():
    """Test bus events forwarding to MCP."""
    print("🧪 Testing Bus -> MCP forwarding...")
    
    # Publish test event to bus
    bus.publish("deploy.success", {
        "dataset": "test.csv",
        "response_time": 1500
    })
    
    # Check if it appears in MCP outbox
    time.sleep(0.1)
    messages = mcp_bridge.get_outbox_messages()
    
    if messages:
        print(f"✅ Found {len(messages)} messages in MCP outbox")
        print(f"   Latest: {messages[-1]['event_type']}")
    else:
        print("❌ No messages in MCP outbox")

def test_mcp_to_bus():
    """Test MCP messages forwarding to bus."""
    print("🧪 Testing MCP -> Bus forwarding...")
    
    # Add test message to MCP inbox
    test_message = {
        "context_id": "ctx_test_001",
        "timestamp": "2025-01-01T10:00:00",
        "event_type": "external.alert",
        "payload": {"message": "Test from MCP"},
        "source": "mcp_agent"
    }
    
    mcp_bridge.add_inbox_message(test_message)
    mcp_bridge.process_mcp_inbox()
    
    # Check if it appears in bus
    bus_messages = bus.get_messages("external.alert")
    
    if bus_messages:
        print(f"✅ Found {len(bus_messages)} messages in bus")
        print(f"   Latest: {bus_messages[-1]['data']}")
    else:
        print("❌ No messages forwarded to bus")

def test_http_endpoints():
    """Test HTTP endpoints (requires server running)."""
    print("🧪 Testing HTTP endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8080/health", timeout=2)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        
        # Test outbox endpoint
        response = requests.get("http://localhost:8080/mcp_outbox", timeout=2)
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ Outbox endpoint working ({len(messages)} messages)")
        
    except requests.exceptions.RequestException:
        print("❌ HTTP endpoints not available (start mcp_endpoints.py)")

if __name__ == "__main__":
    print("🔗 MCP Bridge Integration Test")
    print("=" * 40)
    
    test_bus_to_mcp()
    test_mcp_to_bus()
    test_http_endpoints()
    
    print("\n📋 Integration Summary:")
    print(f"   Bus messages: {len(bus.get_messages())}")
    print(f"   MCP outbox: {len(mcp_bridge.get_outbox_messages())}")
    print("\n💡 To test HTTP endpoints, run: python mcp_endpoints.py")