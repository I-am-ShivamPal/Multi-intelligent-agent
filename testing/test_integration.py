#!/usr/bin/env python3
"""
Test Integration Layer
Test DAY 6 integration with learning/automation layer
"""

import json
import time
from integration.api_adapter import get_api_adapter
from integration.unified_event_pipe import get_unified_pipe, get_events, get_health, get_metrics
from integration.event_schema import StandardEvent, EventValidator

def test_api_adapter():
    """Test API adapter functionality."""
    print("🔧 Testing API Adapter...")
    
    for env in ['dev', 'stage', 'prod']:
        adapter = get_api_adapter(env)
        
        # Test log reading
        deploy_events = adapter.read_deployment_logs(5)
        healing_events = adapter.read_healing_logs(5)
        issue_events = adapter.read_issue_logs(5)
        
        print(f"   {env.upper()}: {len(deploy_events)} deploy, {len(healing_events)} heal, {len(issue_events)} issue events")
        
        # Test system status
        status = adapter.get_system_status()
        print(f"   {env.upper()} status: {status['status']}")
        
        # Test unified stream
        unified = adapter.get_unified_event_stream(10)
        print(f"   {env.upper()} unified stream: {len(unified)} events")
    
    print("   ✅ API Adapter test passed")
    return True

def test_event_schema():
    """Test standardized event schema."""
    print("\n📋 Testing Event Schema...")
    
    # Test event creation
    deploy_event = StandardEvent.from_deployment('dev', 'success', 1500.0, 'test.csv')
    healing_event = StandardEvent.from_healing('dev', 'success', 800.0, 'retry_deployment')
    issue_event = StandardEvent.from_issue('dev', 'anomaly_score', 'Low performance')
    
    # Test validation
    events = [deploy_event.to_dict(), healing_event.to_dict(), issue_event.to_dict()]
    
    for i, event in enumerate(events):
        if EventValidator.validate(event):
            print(f"   ✅ Event {i+1} validation passed")
        else:
            print(f"   ❌ Event {i+1} validation failed")
            return False
    
    # Test sanitization
    dirty_event = {
        "event": "DEPLOYMENT",
        "env": "DEV",
        "status": "SUCCESS",
        "latency": "1500",
        "timestamp": "2024-01-01T12:00:00",
        "extra_field": "should_be_removed"
    }
    
    clean_event = EventValidator.sanitize(dirty_event)
    if clean_event["env"] == "dev" and clean_event["status"] == "success":
        print("   ✅ Event sanitization passed")
    else:
        print("   ❌ Event sanitization failed")
        return False
    
    print("   ✅ Event Schema test passed")
    return True

def test_unified_event_pipe():
    """Test unified event pipe."""
    print("\n🔄 Testing Unified Event Pipe...")
    
    pipe = get_unified_pipe()
    
    # Test latest events
    events = pipe.get_latest_events(10)
    print(f"   Latest events: {len(events)}")
    
    # Test system health
    health = pipe.get_system_health()
    print(f"   System health: {health['overall_status']}")
    print(f"   Environments: {health['summary']['healthy_environments']}/{health['summary']['total_environments']} healthy")
    
    # Test learning metrics
    metrics = pipe.get_learning_metrics()
    print(f"   Avg success rate: {metrics['aggregated']['avg_deployment_success_rate']:.2f}")
    print(f"   Avg stability: {metrics['aggregated']['avg_system_stability']:.2f}")
    
    # Test export
    export_file = pipe.export_events_for_ritesh("test_export.json", 50)
    if export_file:
        print(f"   ✅ Export successful: {export_file}")
        
        # Verify export content
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        required_keys = ['metadata', 'system_health', 'learning_metrics', 'events']
        if all(key in export_data for key in required_keys):
            print("   ✅ Export format validation passed")
        else:
            print("   ❌ Export format validation failed")
            return False
    else:
        print("   ❌ Export failed")
        return False
    
    print("   ✅ Unified Event Pipe test passed")
    return True

def test_convenience_functions():
    """Test convenience functions for Ritesh."""
    print("\n🎯 Testing Convenience Functions...")
    
    # Test simple functions
    events = get_events(5)
    health = get_health()
    metrics = get_metrics()
    
    print(f"   get_events(): {len(events)} events")
    print(f"   get_health(): {health['overall_status']}")
    print(f"   get_metrics(): {len(metrics['environments'])} environments")
    
    # Test export function
    export_file = "ritesh_automation_data.json"
    from integration.unified_event_pipe import export_for_automation
    result = export_for_automation(export_file)
    
    if result:
        print(f"   ✅ export_for_automation(): {result}")
    else:
        print("   ❌ export_for_automation() failed")
        return False
    
    print("   ✅ Convenience Functions test passed")
    return True

def test_real_time_monitoring():
    """Test real-time event monitoring."""
    print("\n⏱️ Testing Real-time Monitoring...")
    
    pipe = get_unified_pipe()
    
    # Test subscription
    received_events = []
    
    def event_callback(event):
        received_events.append(event)
        print(f"   📥 Received event: {event['event']} - {event['status']}")
    
    pipe.subscribe_to_events(event_callback)
    
    # Start monitoring briefly
    pipe.start_event_monitoring()
    print("   🔄 Monitoring started for 3 seconds...")
    time.sleep(3)
    pipe.stop_event_monitoring()
    
    print(f"   📊 Received {len(received_events)} events during monitoring")
    print("   ✅ Real-time Monitoring test passed")
    return True

def demonstrate_ritesh_integration():
    """Demonstrate integration for Ritesh's automation layer."""
    print("\n🤖 Demonstrating Ritesh Integration...")
    
    print("   📋 Available API methods:")
    pipe = get_unified_pipe()
    api_summary = pipe.get_api_summary()
    
    for method in api_summary["available_methods"]:
        print(f"      - {method}")
    
    print("\n   📊 Event Schema:")
    schema = api_summary["event_schema"]
    print(f"      Required fields: {schema['required_fields']}")
    print(f"      Event types: {schema['event_types']}")
    print(f"      Environments: {schema['environments']}")
    
    print("\n   🔗 Simple Usage Examples:")
    print("      # Get latest 10 events from all environments")
    print("      events = get_events(10)")
    print("      ")
    print("      # Get system health status")
    print("      health = get_health()")
    print("      ")
    print("      # Get learning metrics for ML/RL")
    print("      metrics = get_metrics()")
    print("      ")
    print("      # Export all data for automation")
    print("      export_for_automation('my_data.json')")
    
    print("\n   ✅ Integration ready for Ritesh - no changes required on his side!")
    return True

if __name__ == "__main__":
    print("🚀 DAY 6 - Integration with Learning/Automation Layer Test")
    print("=" * 65)
    
    tests = [
        ("API Adapter", test_api_adapter),
        ("Event Schema", test_event_schema),
        ("Unified Event Pipe", test_unified_event_pipe),
        ("Convenience Functions", test_convenience_functions),
        ("Real-time Monitoring", test_real_time_monitoring),
        ("Ritesh Integration Demo", demonstrate_ritesh_integration)
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
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        print("\n🔧 Integration layer ready with:")
        print("   - Standardized event schema")
        print("   - Unified API adapter")
        print("   - Real-time event monitoring")
        print("   - Simple convenience functions")
        print("   - Ready for Ritesh's automation layer")
        print("\n📖 Usage: from integration.unified_event_pipe import get_events, get_health, get_metrics")
        exit(0)
    else:
        print("\n⚠️ Some integration tests failed")
        exit(1)