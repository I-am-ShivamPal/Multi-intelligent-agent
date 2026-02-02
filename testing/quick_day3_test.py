#!/usr/bin/env python3
"""
Quick Day 3 Test - Minimal validation
"""

import time
import os
from datetime import datetime

def test_basic_functionality():
    """Test basic Day 3 components"""
    print("🧪 Quick Day 3 Validation")
    print("=" * 40)
    
    # Test 1: Import modules
    try:
        from core.realtime_bus import RealtimeBus
        from agents.multi_deploy_agent import MultiDeployAgent, ScalingSimulator
        print("✅ Modules import successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test 2: Create bus and publish message
    try:
        bus = RealtimeBus()
        bus.publish('test', {'message': 'hello'})
        stats = bus.get_stats()
        assert stats['total_messages'] >= 1
        print("✅ Real-time bus works")
    except Exception as e:
        print(f"❌ Bus error: {e}")
        return False
    
    # Test 3: Create deploy agent
    try:
        agent = MultiDeployAgent(agent_id=1)
        thread = agent.start()
        time.sleep(1)
        agent.stop()
        print("✅ Multi-deploy agent works")
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False
    
    # Test 4: Check performance log creation
    try:
        log_file = os.path.join("logs", r"performance_log.csv")
        if os.path.exists(log_file):
            print("✅ Performance log created")
        else:
            print("⚠️ Performance log not found (will be created on first run)")
    except Exception as e:
        print(f"❌ Log error: {e}")
        return False
    
    print("\n🎉 Day 3 components are working!")
    return True

if __name__ == "__main__":
    test_basic_functionality()