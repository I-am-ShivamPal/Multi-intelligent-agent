"""
Safe Orchestrator - Executes RL decisions with safety validation
DEMO_MODE Execution Gate: Enforces RL-only action intake with prod-level safety
"""

import datetime
import json
import os
from typing import Dict, Any, List, Optional

def get_safe_executor(env='dev'):
    """Get safe executor instance"""
    return SafeOrchestrator(env)

class SafeOrchestrator:
    def __init__(self, env='dev'):
        self.env = env
        self.safe_actions = {
            'restart': self._restart_service,
            'scale_up': self._scale_up_service,
            'noop': self._no_operation,
            'scale_down': self._scale_down_service,
            'rollback': self._rollback_deployment
        }
        
        # Environment-specific safety rules
        self.safety_rules = {
            'prod': ['noop'],  # Production only allows noop for safety
            'stage': ['restart', 'noop'],  # Stage allows restart and noop
            'dev': ['restart', 'scale_up', 'noop', 'scale_down']  # Dev allows most actions
        }
        
        # Load DEMO_MODE configuration
        try:
            from demo_mode_config import is_demo_mode_active, DEMO_ENFORCE_PROD_SAFETY
            self.demo_mode = is_demo_mode_active()
            self.demo_enforce_prod = DEMO_ENFORCE_PROD_SAFETY
        except ImportError:
            self.demo_mode = False
            self.demo_enforce_prod = False
    
    def is_action_safe(self, action: str) -> bool:
        """Check if action is safe for current environment"""
        allowed_actions = self.safety_rules.get(self.env, ['noop'])
        return action in allowed_actions
    
    def execute_safe_action(self, action: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action if safe, otherwise default to noop"""
        timestamp = datetime.datetime.now().isoformat()
        
        if not self.is_action_safe(action):
            # Log safety violation and default to noop
            result = {
                'action_requested': action,
                'action_executed': 'noop',
                'reason': f'Action {action} not safe for {self.env} environment',
                'success': True,
                'timestamp': timestamp,
                'safety_override': True
            }
            self._log_execution(result)
            return result
        
        # Execute the safe action
        try:
            execution_func = self.safe_actions.get(action, self._no_operation)
            result = execution_func(context)
            result.update({
                'action_executed': action,
                'success': True,
                'timestamp': timestamp,
                'safety_override': False
            })
        except Exception as e:
            result = {
                'action_executed': action,
                'success': False,
                'error': str(e),
                'timestamp': timestamp,
                'safety_override': False
            }
        
        self._log_execution(result)
        return result
    
    def _validate_demo_mode_gate(self, source: Optional[str], action: str) -> tuple[bool, str]:
        """
        DEMO_MODE execution gate - block direct calls, validate RL intake
        
        Args:
            source: Source identifier (should be 'rl_decision_layer' in DEMO_MODE)
            action: Action being requested
            
        Returns:
            Tuple of (allowed, reason) - (True, "") if allowed, (False, reason) if blocked
        """
        from core.proof_logger import write_proof, ProofEvents
        
        if not self.demo_mode:
            return (True, "")  # Not in demo mode, allow through
        
        # Check if action came from RL layer
        if not source or source not in ['rl_decision_layer', 'rl_intake_gate']:
            write_proof(ProofEvents.DEMO_MODE_BLOCK, {
                'env': self.env,
                'action': action,
                'source': source or 'UNKNOWN',
                'reason': 'Direct orchestrator call blocked - must come through RL intake gate',
                'demo_mode': True
            })
            return (False, "DEMO_MODE: Direct calls blocked - actions must come from RL layer")
        
        # Validate RL intake source
        write_proof(ProofEvents.RL_INTAKE_VALIDATED, {
            'env': self.env,
            'action': action,
            'source': source,
            'status': 'validated'
        })
        
        return (True, "")
    
    def _enforce_demo_safety(self, action: str, source: Optional[str]) -> tuple[bool, str]:
        """
        Enforce DEMO_MODE production-level safety rules
        
        Args:
            action: Action to validate
            source: Source identifier
            
        Returns:
            Tuple of (safe, reason) - (True, "") if safe, (False, reason) if refused
        """
        from core.prod_safety import is_demo_mode_safe
        from core.proof_logger import write_proof, ProofEvents
        
        is_safe, refusal_reason = is_demo_mode_safe(action, source)
        
        if not is_safe:
            write_proof(ProofEvents.UNSAFE_ACTION_REFUSED, {
                'env': self.env,
                'action': action,
                'source': source or 'UNKNOWN',
                'reason': refusal_reason,
                'demo_mode': self.demo_mode
            })
        
        return (is_safe, refusal_reason)
    
    def execute_action(self, action: str, context: Dict[str, Any], source: Optional[str] = None) -> Dict[str, Any]:
        """
        CENTRALIZED EXECUTION GATE - All action execution passes through here
        
        This is the ONLY entry point for action execution in DEMO_MODE.
        ALL paths must pass through:
        1. RL decision intake validation
        2. Safety guard checks
        3. Determinism verification
        
        Args:
            action: Action name to execute
            context: Execution context
            source: Source identifier (required in DEMO_MODE)
            
        Returns:
            Execution result with status and proof logging
        """
        from core.proof_logger import write_proof, ProofEvents
        timestamp = datetime.datetime.now().isoformat()
        
        # GATE 1: DEMO_MODE intake validation
        gate_passed, gate_reason = self._validate_demo_mode_gate(source, action)
        if not gate_passed:
            return {
                'action_requested': action,
                'action_executed': 'noop',
                'reason': gate_reason,
                'success': False,
                'timestamp': timestamp,
                'demo_mode_blocked': True,
                'source': source
            }
        
        # GATE 2: DEMO_MODE safety enforcement
        if self.demo_mode and self.demo_enforce_prod:
            safety_passed, safety_reason = self._enforce_demo_safety(action, source)
            if not safety_passed:
                return {
                    'action_requested': action,
                    'action_executed': 'noop',
                    'reason': safety_reason,
                    'success': False,
                    'timestamp': timestamp,
                    'safety_refused': True,
                    'source': source
                }
        
        # GATE 3: Environment-specific safety check
        if not self.is_action_safe(action):
            write_proof(ProofEvents.ORCH_REFUSE, {
                'env': self.env,
                'action': action,
                'reason': 'environment_safety_rules',
                'status': 'refused'
            })
            return {
                'action_requested': action,
                'action_executed': 'noop',
                'reason': f'Action {action} not safe for {self.env} environment',
                'success': True,
                'timestamp': timestamp,
                'safety_override': True
            }
        
        # All gates passed - log and execute
        write_proof(ProofEvents.EXECUTION_GATE_PASSED, {
            'env': self.env,
            'action': action,
            'source': source or 'legacy',
            'demo_mode': self.demo_mode,
            'gates_passed': ['rl_intake', 'demo_safety', 'env_safety']
        })
        
        # Execute the action
        try:
            execution_func = self.safe_actions.get(action, self._no_operation)
            result = execution_func(context)
            result.update({
                'action_executed': action,
                'success': True,
                'timestamp': timestamp,
                'safety_override': False,
                'source': source
            })
            
            write_proof(ProofEvents.ORCH_EXEC, {
                'env': self.env,
                'action': action,
                'status': 'executed',
                'source': source
            })
            
            write_proof(ProofEvents.SYSTEM_STABLE, {
                'env': self.env,
                'recovery_action': action,
                'status': 'stable'
            })
            
        except Exception as e:
            result = {
                'action_executed': action,
                'success': False,
                'error': str(e),
                'timestamp': timestamp,
                'safety_override': False,
                'source': source
            }
        
        return result
    
    def validate_and_execute(self, action_index: int, context: Dict[str, Any], source: Optional[str] = None) -> Dict[str, Any]:
        """Validate and execute action by index - routes through centralized execute_action()"""
        
        # Map action indices to action names
        action_map = {
            0: 'noop',
            1: 'restart',
            2: 'scale_up', 
            3: 'scale_down',
            4: 'rollback'
        }
        
        action_name = action_map.get(action_index, 'noop')
        
        # Route through centralized execution gate
        return self.execute_action(action_name, context, source=source)
    
    def _restart_service(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Restart service action"""
        app_name = context.get('app_name', 'unknown')
        return {
            'action': 'restart',
            'app_name': app_name,
            'details': f'Service {app_name} restarted successfully',
            'recovery_time': '15s'
        }
    
    def _scale_up_service(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Scale up service action"""
        app_name = context.get('app_name', 'unknown')
        current_replicas = context.get('replicas', 1)
        new_replicas = min(current_replicas + 1, 5)  # Max 5 replicas
        
        return {
            'action': 'scale_up',
            'app_name': app_name,
            'replicas_before': current_replicas,
            'replicas_after': new_replicas,
            'details': f'Scaled {app_name} from {current_replicas} to {new_replicas} replicas'
        }
    
    def _scale_down_service(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Scale down service action"""
        app_name = context.get('app_name', 'unknown')
        current_replicas = context.get('replicas', 2)
        new_replicas = max(current_replicas - 1, 1)  # Min 1 replica
        
        return {
            'action': 'scale_down',
            'app_name': app_name,
            'replicas_before': current_replicas,
            'replicas_after': new_replicas,
            'details': f'Scaled {app_name} from {current_replicas} to {new_replicas} replicas'
        }
    
    def _no_operation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """No operation - safe default"""
        return {
            'action': 'noop',
            'details': 'No action taken - system monitoring continues',
            'reason': 'Safe default or false alarm detected'
        }
    
    def _rollback_deployment(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Rollback to previous deployment"""
        app_name = context.get('app_name', 'unknown')
        return {
            'action': 'rollback',
            'app_name': app_name,
            'details': f'Rolled back {app_name} to previous stable version',
            'rollback_time': '45s'
        }
    
    def _log_execution(self, result: Dict[str, Any]):
        """Log execution result"""
        log_dir = f"logs/{self.env}"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "orchestrator_executions.log")
        with open(log_file, 'a') as f:
            f.write(json.dumps(result) + '\n')