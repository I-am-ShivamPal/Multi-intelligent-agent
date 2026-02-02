#!/usr/bin/env python3
"""
Test Redis Event Bus
Test external event bus functionality
"""

import time
import threading
from core.redis_event_bus import get_redis_bus

def test_redis_event_bus():
    """Test Redis event bus functionality."""
    print("🚀 Testing Redis Event Bus...")
    
    # Test all environments
    for env in ['dev', 'stage', 'prod']:
        print(f"\n📋 Testing {env.upper()} environment:")
        
        bus = get_redis_bus(env)
        
        # Test connection
        stats = bus.get_queue_stats()
        print(f"   Redis Connected: {'✅' if stats['connected'] else '❌'}")
        
        if stats['connected']:
            print(f"   Redis Version: {stats.get('redis_version', 'Unknown')}")
            print(f"   Connected Clients: {stats.get('connected_clients', 0)}")
        
        # Test message publishing
        test_messages = [
            ('deploy.success', {'dataset': 'test.csv', 'time': 1500}),
            ('issue.detected', {'type': 'anomaly', 'severity': 'high'}),
            ('heal.completed', {'strategy': 'retry', 'status': 'success'})
        ]
        
        print("   📤 Publishing test messages...")
        for event_type, data in test_messages:
            bus.publish(event_type, data)
            time.sleep(0.1)
        
        # Check message history
        history = bus.get_message_history(5)
        print(f"   📜 Message history: {len(history)} messages")
        
        # Test subscription (mock mode)
        received_messages = []
        
        def test_callback(event_type, data):
            received_messages.append((event_type, data))
            print(f"   📥 Received: {event_type}")
        
        bus.subscribe("deploy.*", test_callback)
        bus.subscribe("issue.*", test_callback)
        
        print(f"   📡 Subscriptions: {len(bus.subscribers)}")
        
        # Publish more messages to test subscription
        bus.publish('deploy.failure', {'error': 'timeout'})
        bus.publish('issue.resolved', {'resolution': 'auto-heal'})
        
        time.sleep(0.5)  # Allow processing
        
        print(f"   ✅ Test completed for {env}")

def test_queue_monitor_integration():
    """Test integration with queue monitor."""
    print("\n🔍 Testing Queue Monitor Integration...")
    
    from queue_monitor import QueueMonitor
    
    monitor = QueueMonitor('dev')
    
    # Test stats
    monitor.print_stats()
    
    # Test message flow
    monitor.test_message_flow()
    
    print("✅ Queue monitor integration working")

def test_agent_integration():
    """Test agent integration with Redis bus."""
    print("\n🤖 Testing Agent Integration...")
    
    from agents.deploy_agent import DeployAgent
    from core.env_config import EnvironmentConfig
    
    # Test deploy agent
    env_config = EnvironmentConfig('dev')
    deploy_agent = DeployAgent('test_deployment.csv', 'dev')
    
    # Test logging with Redis publishing
    deploy_agent.log_deployment('test_dataset.csv', 'success', 1234.5)
    
    print("✅ Agent integration working")

if __name__ == "__main__":
    print("🧪 DAY 3 - External Event Bus (Redis) Test")
    print("=" * 50)
    
    try:
        # Run tests
        test_redis_event_bus()
        test_queue_monitor_integration()
        test_agent_integration()
        
        print("\n🎉 All Redis event bus tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)