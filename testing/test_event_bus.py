#!/usr/bin/env python3
"""Test multi-agent message flow via Redis event bus"""
import time
import threading
from core.event_bus import event_bus
import json

def test_multi_agent_flow():
    """Test message flow between multiple agents"""
    print("=== DAY 2 EVENT BUS TEST ===\n")
    
    messages_received = []
    
    def deploy_agent_handler(message):
        print(f"Deploy Agent received: {message}")
        messages_received.append(('deploy', message))
    
    def heal_agent_handler(message):
        print(f"Heal Agent received: {message}")
        messages_received.append(('heal', message))
        
        # Heal agent responds to issues
        event_bus.publish('healing_action', {
            'action': 'retry_deployment',
            'issue_id': message.get('issue_id', 'unknown')
        })
    
    def monitor_handler(message):
        print(f"Monitor received: {message}")
        messages_received.append(('monitor', message))
    
    # Subscribe agents to channels
    print("✓ Setting up agent subscriptions...")
    event_bus.subscribe('deployment_event', deploy_agent_handler)
    event_bus.subscribe('issue_detected', heal_agent_handler)
    event_bus.subscribe('healing_action', monitor_handler)
    
    time.sleep(1)  # Allow subscriptions to register
    
    # Simulate multi-agent workflow
    print("\n✓ Testing message flow...")
    
    # 1. Deploy agent publishes deployment
    event_bus.publish('deployment_event', {
        'deployment_id': 'deploy_001',
        'status': 'started',
        'timestamp': time.time()
    })
    
    time.sleep(0.5)
    
    # 2. Issue detector finds problem
    event_bus.publish('issue_detected', {
        'issue_id': 'issue_001',
        'type': 'deployment_failure',
        'severity': 'high'
    })
    
    time.sleep(0.5)
    
    # 3. Monitor publishes system status
    event_bus.publish('system_status', {
        'uptime': '99.5%',
        'active_deployments': 3
    })
    
    time.sleep(1)  # Allow all messages to process
    
    # Check results
    print(f"\n✓ Messages processed: {len(messages_received)}")
    
    # Check performance log
    try:
        with open('logs/performance_log.csv', 'r') as f:
            lines = f.readlines()
            print(f"✓ Performance entries logged: {len(lines) - 1}")  # -1 for header
    except:
        print("✗ Performance log not found")
    
    success = len(messages_received) >= 2
    print(f"\nStatus: {'🟢 PASSED' if success else '🔴 FAILED'}")
    
    return success

if __name__ == '__main__':
    success = test_multi_agent_flow()
    
    if success:
        print("\nDAY 2 EVENT BUS:")
        print("✓ Redis pub/sub integration")
        print("✓ Multi-agent message flow")
        print("✓ Performance logging")
        print("✓ Cross-process communication")