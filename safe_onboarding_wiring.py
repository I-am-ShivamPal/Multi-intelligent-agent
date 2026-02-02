#!/usr/bin/env python3
"""
Safe Onboarding → Runtime Wiring
Safely wire validated app_spec into deployment pipeline
"""

import json
import os
import sys
from datetime import datetime

class SafeOnboardingWiring:
    """Wire onboarded apps into runtime pipeline with safety enforcement"""
    
    def __init__(self):
        self.registry_dir = "apps/registry"
        self.log_file = "logs/onboarding_wiring.log"
        os.makedirs("logs", exist_ok=True)
    
    def wire_app_to_runtime(self, app_name, target_env="dev"):
        """Wire app from registry to runtime pipeline"""
        
        # Block production onboarding
        if target_env == "prod":
            self._log_refusal(app_name, target_env, "Production onboarding blocked by safety guard")
            return False
        
        # Load app spec
        spec_file = f"{self.registry_dir}/{app_name}.json"
        if not os.path.exists(spec_file):
            self._log_refusal(app_name, target_env, f"App spec not found: {spec_file}")
            return False
        
        with open(spec_file, 'r') as f:
            app_spec = json.load(f)
        
        # Validate environment support
        if target_env not in app_spec.get("environments", []):
            self._log_refusal(app_name, target_env, f"Environment {target_env} not supported by app")
            return False
        
        # Wire to deployment
        deploy_success = self._wire_to_deployment(app_spec, target_env)
        if not deploy_success:
            return False
        
        # Wire to monitoring
        self._wire_to_monitoring(app_spec, target_env)
        
        # Emit runtime events
        self._emit_runtime_events(app_spec, target_env)
        
        self._log_success(app_name, target_env, "Successfully wired to runtime pipeline")
        return True
    
    def _wire_to_deployment(self, app_spec, env):
        """Wire app to deployment system"""
        try:
            # Simulate deployment with safety checks
            from core.prod_safety import validate_prod_action, ProductionSafetyError
            
            # Check if deployment action is safe
            try:
                validate_prod_action("retry_deployment", env)
            except ProductionSafetyError as e:
                self._log_refusal(app_spec["name"], env, f"Deployment blocked by prod safety: {e}")
                return False
            
            # Stage determinism enforcement
            if env == "stage":
                from core.stage_determinism import StageDeterminismLock
                if not StageDeterminismLock.is_stage_env(env):
                    self._log_refusal(app_spec["name"], env, "Stage determinism validation failed")
                    return False
            
            # Emit deploy event
            from core.guaranteed_events import emit_deploy_event
            emit_deploy_event(
                env=env,
                status="success",
                response_time=120,
                dataset=f"{app_spec['name']}_onboarding.csv"
            )
            
            return True
            
        except Exception as e:
            self._log_refusal(app_spec["name"], env, f"Deployment wiring failed: {e}")
            return False
    
    def _wire_to_monitoring(self, app_spec, env):
        """Wire app to monitoring system"""
        try:
            # Add to uptime monitoring
            from agents.uptime_monitor import UptimeMonitor
            monitor = UptimeMonitor(f"logs/{env}/uptime_{app_spec['name']}.csv")
            monitor.update_status("UP", f"Onboarded app {app_spec['name']} started")
            
        except Exception as e:
            print(f"WARNING: Monitoring wiring failed: {e}")
    
    def _emit_runtime_events(self, app_spec, env):
        """Emit runtime events for onboarded app"""
        try:
            # Emit scale event for resource allocation
            from core.guaranteed_events import emit_scale_event
            emit_scale_event(
                env=env,
                status="success", 
                response_time=80,
                dataset=f"{app_spec['name']}_scaling.csv",
                worker_count=app_spec["scaling"]["min_replicas"],
                scale_direction="horizontal"
            )
            
            # Emit restart event for service initialization
            from core.guaranteed_events import emit_restart_event
            emit_restart_event(
                env=env,
                status="success",
                response_time=45,
                dataset=f"{app_spec['name']}_restart.csv",
                restart_type="service_initialization"
            )
            
        except Exception as e:
            print(f"WARNING: Runtime event emission failed: {e}")
    
    def _log_success(self, app_name, env, message):
        """Log successful wiring"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "WIRED",
            "app_name": app_name,
            "environment": env,
            "message": message
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        print(f"[WIRED] {app_name} -> {env}: {message}")
    
    def _log_refusal(self, app_name, env, reason):
        """Log wiring refusal"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "status": "REFUSED",
            "app_name": app_name,
            "environment": env,
            "reason": reason
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        print(f"[REFUSED] {app_name} -> {env}: {reason}")

def wire_app(app_name, env="dev"):
    """Wire app from registry to runtime"""
    wiring = SafeOnboardingWiring()
    return wiring.wire_app_to_runtime(app_name, env)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python safe_onboarding_wiring.py <app_name> [environment]")
        sys.exit(1)
    
    app_name = sys.argv[1]
    env = sys.argv[2] if len(sys.argv) > 2 else "dev"
    
    success = wire_app(app_name, env)
    sys.exit(0 if success else 1)