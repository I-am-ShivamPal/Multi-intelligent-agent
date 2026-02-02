#!/usr/bin/env python3
"""
Onboarding Entry Layer - Text to Spec Conversion
Converts simple text input to validated app_spec.json

Principles:
- No intelligence/inference/guessing
- Template-based conversion only
- Deterministic validation
- Clear error messages
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class OnboardingEntry:
    def __init__(self):
        self.output_dir = "apps/registry"
        self.log_file = "logs/onboarding.log"
        self.proof_log = "logs/onboarding_proof.log"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # Import proof logger
        try:
            from core.proof_logger import write_proof, ProofEvents
            self.proof_logger = write_proof
            self.ProofEvents = ProofEvents
            self.use_proof_logging = True
        except ImportError:
            self.use_proof_logging = False
    
    def process(self, repo_url: str, app_name: str, runtime_type: str) -> bool:
        """Convert input to app_spec.json with validation"""
        
        # Log onboarding start
        self._log_proof(self.ProofEvents.ONBOARDING_STARTED if self.use_proof_logging else None, {
            'app_name': app_name,
            'runtime_type': runtime_type,
            'repo_url': repo_url[:100]  # Truncate for logging
        })
        
        # Validate input (deterministic, no guessing)
        is_valid, error_message = self._validate_input(repo_url, app_name, runtime_type)
        if not is_valid:
            self._log_proof(self.ProofEvents.ONBOARDING_REJECTED if self.use_proof_logging else None, {
                'app_name': app_name,
                'reason': error_message
            })
            self._log("REJECTED", {"repo_url": repo_url, "app_name": app_name, "runtime_type": runtime_type}, error_message)
            return False
        
        # Log validation passed
        self._log_proof(self.ProofEvents.ONBOARDING_VALIDATION_PASSED if self.use_proof_logging else None, {
            'app_name': app_name,
            'runtime_type': runtime_type
        })
        
        # Generate app_spec (template-based, no intelligence)
        app_spec = self._generate_spec(repo_url, app_name, runtime_type)
        
        # Save to registry
        output_file = f"{self.output_dir}/{app_name}.json"
        with open(output_file, 'w') as f:
            json.dump(app_spec, f, indent=2)
        
        # Log spec generated
        self._log_proof(self.ProofEvents.SPEC_GENERATED if self.use_proof_logging else None, {
            'app_name': app_name,
            'spec_file': output_file
        })
        
        self._log("ACCEPTED", {"repo_url": repo_url, "app_name": app_name, "runtime_type": runtime_type}, output_file)
        
        # Trigger deployment
        self._trigger_deployment(app_name, output_file)
        
        return True
    
    def _validate_input(self, repo_url: str, app_name: str, runtime_type: str) -> tuple[bool, Optional[str]]:
        """Validate input parameters (deterministic, no guessing)
        
        Returns:
            tuple: (is_valid, error_message)
        """
        
        # App name validation - strict lowercase alphanumeric with hyphens
        if not re.match(r'^[a-z0-9-]{3,50}$', app_name):
            return (False, "Invalid app name: must be 3-50 lowercase alphanumeric characters with hyphens only")
        
        # Check app name uniqueness
        spec_file = f"{self.output_dir}/{app_name}.json"
        if os.path.exists(spec_file):
            return (False, f"App name '{app_name}' already exists in registry")
        
        # Runtime type validation - strict enum
        if runtime_type not in ['backend', 'frontend', 'fullstack']:
            return (False, f"Invalid runtime type '{runtime_type}': must be 'backend', 'frontend', or 'fullstack'")
        
        # URL protocol validation
        if not (repo_url.startswith('http://') or repo_url.startswith('https://')):
            return (False, "Invalid repo URL: must start with http:// or https://")
        
        # Repo URL length check
        if len(repo_url) > 500:
            return (False, "Invalid repo URL: exceeds maximum length of 500 characters")
        
        # Repo URL safety check - prevent file:// and local paths
        if repo_url.startswith('file://'):
            return (False, "Invalid repo URL: file:// protocol not allowed")
        
        # Check for shell injection patterns
        unsafe_patterns = ['../', '/etc/', '/var/', 'rm ', 'del ', ';', '&&', '|', '`', '$(']
        for pattern in unsafe_patterns:
            if pattern in repo_url:
                return (False, f"Invalid repo URL: contains unsafe pattern '{pattern}'")
        
        return (True, None)
    
    def _generate_spec(self, repo_url, app_name, runtime_type):
        """Generate app_spec.json from input"""
        
        defaults = {
            'backend': {
                'build_command': 'pip install -r requirements.txt',
                'start_command': 'python app.py',
                'health_endpoint': '/health',
                'port': 5000
            },
            'frontend': {
                'build_command': 'npm install && npm run build',
                'start_command': 'npm start',
                'health_endpoint': '/index.html',
                'port': 3000
            },
            'fullstack': {
                'build_command': 'npm install && pip install -r requirements.txt',
                'start_command': 'npm run start:prod',
                'health_endpoint': '/api/health',
                'port': 8080
            }
        }
        
        config = defaults[runtime_type]
        
        return {
            "name": app_name,
            "type": runtime_type,
            "repo_path_or_url": repo_url,
            "build_command": config['build_command'],
            "start_command": config['start_command'],
            "health_endpoint": config['health_endpoint'],
            "environments": ["dev", "stage", "prod"],
            "port": config['port'],
            "resources": {
                "cpu": "0.5",
                "memory": "512Mi"
            },
            "scaling": {
                "min_replicas": 1,
                "max_replicas": 3,
                "target_cpu_percent": 70
            }
        }
    
    def _log_proof(self, event_type, data: Dict[str, Any]):
        """Log proof event if proof logging is enabled"""
        if not self.use_proof_logging or event_type is None:
            return
        
        try:
            self.proof_logger(event_type, data)
        except Exception:
            pass  # Silent fail if proof logging unavailable
    
    def _trigger_deployment(self, app_name: str, spec_file: str):
        """Trigger deployment for onboarded app"""
        # Log deployment trigger
        self._log_proof(self.ProofEvents.DEPLOYMENT_TRIGGERED if self.use_proof_logging else None, {
            'app_name': app_name,
            'spec_file': spec_file,
            'trigger_source': 'onboarding_entry'
        })
        
        print(f"✓ Deployment triggered for '{app_name}'")
        print(f"  Spec file: {spec_file}")
        print(f"  Ready for pipeline integration")
    
    def _log(self, status: str, input_data: Dict[str, Any], result: str):
        """Log acceptance/rejection"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "input": input_data,
            "result": result
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        # Color-coded output
        status_symbol = "✅" if status == "ACCEPTED" else "❌"
        print(f"{status_symbol} [{status}] {result}")

def cli_interface():
    """Command line interface"""
    print("=== App Onboarding Entry ===")
    
    repo_url = input("Repository URL: ").strip()
    app_name = input("App name: ").strip()
    runtime_type = input("Runtime type (backend/frontend/fullstack): ").strip()
    
    onboarder = OnboardingEntry()
    success = onboarder.process(repo_url, app_name, runtime_type)
    
    if success:
        print(f"App spec generated: apps/registry/{app_name}.json")
    
    return success

def json_interface(input_file):
    """JSON file interface"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    onboarder = OnboardingEntry()
    return onboarder.process(
        data['repo_url'],
        data['app_name'], 
        data['runtime_type']
    )

if __name__ == "__main__":
    if len(sys.argv) > 1:
        success = json_interface(sys.argv[1])
    else:
        success = cli_interface()
    
    sys.exit(0 if success else 1)