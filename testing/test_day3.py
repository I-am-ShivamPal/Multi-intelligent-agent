#!/usr/bin/env python3
"""
Day 3 Testing Script - Real-Time Event Bus & Auto-Scaling
"""

import time
import threading
from core.realtime_bus import realtime_bus
from agents.multi_deploy_agent import scaling_simulator

def test_realtime_bus():
    """Test real-time event bus functionality"""
    print("🧪 Testing Real-Time Event Bus...")
    
    # Create fresh bus instance for testing
    from core.realtime_bus import RealtimeBus
    test_bus = RealtimeBus()
    
    # Test message publishing and subscribing
    messages_received = []
    
    def test_handler(message):
        messages_received.append(message)
    
    test_bus.subscribe('test_topic', test_handler)
    
    # Publish test messages
    for i in range(5):
        test_bus.publish('test_topic', {
            'type': 'test_message',
            'id': i,
            'data': f'Test message {i}'
        })
    
    time.sleep(0.1)  # Allow processing
    
    assert len(messages_received) == 5, f"Expected 5 messages, got {len(messages_received)}"
    print("✅ Event bus messaging works")
    
    # Test performance logging
    stats = test_bus.get_stats()
    assert stats['total_messages'] >= 5, "Performance tracking works"
    print("✅ Performance logging works")

def test_multi_deploy_agents():
    """Test multiple deploy agents"""
    print("🧪 Testing Multi-Deploy Agents...")
    
    # Start 2 agents for testing
    scaling_simulator.num_agents = 2
    agents = scaling_simulator.start_simulation()
    
    assert len(agents) == 2, "Should create 2 agents"
    print("✅ Multiple agents created")
    
    # Let them run briefly
    time.sleep(3)
    
    # Check deployment activity
    stats = scaling_simulator.get_stats()
    assert stats['active_agents'] == 2, "Both agents should be active"
    print("✅ Agents are running concurrently")
    
    # Stop agents
    scaling_simulator.stop_simulation()
    print("✅ Agents stopped successfully")

def test_performance_logging():
    """Test performance log generation"""
    print("🧪 Testing Performance Logging...")
    
    import os
    import pandas as pd
    
    # Check if performance log exists
    log_file = os.path.join("logs", r"performance_log.csv")
    assert os.path.exists(log_file), "Performance log should exist"
    
    # Read and validate log
    df = pd.read_csv(log_file)
    required_columns = ['timestamp', 'event_type', 'throughput_per_sec', 'queue_size', 'total_messages']
    
    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"
    
    print("✅ Performance log format is correct")
    print(f"✅ Log contains {len(df)} entries")

def run_day3_tests():
    """Run all Day 3 tests"""
    print("🚀 Day 3: Real-Time Event Bus & Auto-Scaling Tests")
    print("=" * 60)
    
    try:
        test_realtime_bus()
        test_multi_deploy_agents()
        test_performance_logging()
        
        print("\n🎉 All Day 3 tests passed!")
        print("✅ Real-time event bus working")
        print("✅ Multi-agent scaling working")
        print("✅ Performance logging working")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    run_day3_tests()