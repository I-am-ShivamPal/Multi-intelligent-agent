#!/usr/bin/env python3
"""Test environment configuration"""

try:
    from core.env_config import EnvironmentConfig
    
    # Test dev environment
    dev_config = EnvironmentConfig('dev')
    print(f"✅ DEV environment loaded: {dev_config.get('environment')}")
    print(f"   Log path: {dev_config.get_log_path('test.log')}")
    
    # Test stage environment  
    stage_config = EnvironmentConfig('stage')
    print(f"✅ STAGE environment loaded: {stage_config.get('environment')}")
    
    # Test prod environment
    prod_config = EnvironmentConfig('prod')
    print(f"✅ PROD environment loaded: {prod_config.get('environment')}")
    
    print("\n🎉 Multi-environment configuration working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Installing python-dotenv...")
    import subprocess
    subprocess.run(["pip", "install", "python-dotenv"])
    print("Please run the test again.")