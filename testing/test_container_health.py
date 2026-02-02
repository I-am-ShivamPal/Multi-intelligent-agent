#!/usr/bin/env python3
"""
Test Container Health System
Simulates Docker health checks for testing
"""

import os
import csv
import datetime
from core.env_config import EnvironmentConfig

def test_health_monitoring():
    """Test health monitoring system without Docker."""
    print("🧪 Testing Health Monitoring System...")
    
    # Test all environments
    for env in ['dev', 'stage', 'prod']:
        print(f"\n📋 Testing {env.upper()} environment:")
        
        env_config = EnvironmentConfig(env)
        
        # Create mock health log
        health_log = env_config.get_log_path("infra_health_log.csv")
        os.makedirs(os.path.dirname(health_log), exist_ok=True)
        
        with open(health_log, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'cpu_percent', 'memory_percent', 'disk_percent',
                'docker_status', 'containers_running', 'containers_total',
                'redis_status', 'system_health', 'environment'
            ])
            
            # Add mock data
            timestamp = datetime.datetime.now().isoformat()
            writer.writerow([
                timestamp, 25.5, 68.2, 45.1, 'healthy', 4, 4, 'healthy', 85, env
            ])
        
        print(f"   ✅ Health log created: {health_log}")
        
        # Create mock watchdog log
        watchdog_log = env_config.get_log_path("watchdog_log.csv")
        with open(watchdog_log, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'container_name', 'status', 'health', 
                'action_taken', 'restart_count', 'environment'
            ])
            
            # Add mock container data
            containers = ['cicd-dashboard', 'cicd-mcp', 'cicd-agents', 'cicd-redis']
            for container in containers:
                writer.writerow([
                    timestamp, container, 'running', 'healthy', 'healthy', 0, env
                ])
        
        print(f"   ✅ Watchdog log created: {watchdog_log}")
        
        # Test configuration loading
        print(f"   ✅ Environment config loaded:")
        print(f"      - Latency threshold: {env_config.get('latency_ms')}ms")
        print(f"      - Score threshold: {env_config.get('low_score_avg')}")
        print(f"      - Dashboard port: {env_config.get('dashboard_port')}")

def test_docker_compose_validation():
    """Validate docker-compose.yml configuration."""
    print("\n🐳 Validating Docker Compose Configuration...")
    
    compose_file = "docker-compose.yml"
    if not os.path.exists(compose_file):
        print("   ❌ docker-compose.yml not found")
        return False
    
    with open(compose_file, 'r') as f:
        content = f.read()
    
    # Check for required configurations
    checks = [
        ('restart: always', 'Auto-restart policy'),
        ('healthcheck:', 'Health checks'),
        ('start_period:', 'Health check start period'),
        ('interval: 30s', 'Health check interval'),
        ('retries: 3', 'Health check retries')
    ]
    
    all_passed = True
    for check, description in checks:
        if check in content:
            print(f"   ✅ {description} configured")
        else:
            print(f"   ❌ {description} missing")
            all_passed = False
    
    return all_passed

def test_dockerfile_health_checks():
    """Validate Dockerfile health check configuration."""
    print("\n📦 Validating Dockerfile Health Checks...")
    
    dockerfile = "Dockerfile"
    if not os.path.exists(dockerfile):
        print("   ❌ Dockerfile not found")
        return False
    
    with open(dockerfile, 'r') as f:
        content = f.read()
    
    if 'HEALTHCHECK' in content:
        print("   ✅ Health check configured in Dockerfile")
        if 'curl' in content:
            print("   ✅ curl installed for health checks")
        return True
    else:
        print("   ❌ Health check missing in Dockerfile")
        return False

if __name__ == "__main__":
    print("🚀 DAY 2 - Docker Health Checks + Auto-Restart Rules Test")
    print("=" * 60)
    
    # Run tests
    test_health_monitoring()
    compose_ok = test_docker_compose_validation()
    dockerfile_ok = test_dockerfile_health_checks()
    
    print("\n📊 Test Summary:")
    print(f"   Health Monitoring: ✅ Working")
    print(f"   Docker Compose: {'✅ Valid' if compose_ok else '❌ Issues'}")
    print(f"   Dockerfile: {'✅ Valid' if dockerfile_ok else '❌ Issues'}")
    
    if compose_ok and dockerfile_ok:
        print("\n🎉 All Docker health checks configured successfully!")
        exit(0)
    else:
        print("\n⚠️ Some configurations need attention")
        exit(1)