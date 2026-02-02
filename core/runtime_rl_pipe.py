#!/usr/bin/env python3
"""
Runtime → RL Direct Pipe
Pipes normalized runtime JSON to Ritesh's RL layer unchanged and live
"""

from core.rl_decision_layer import RLDecisionLayer

class RuntimeRLPipe:
    """Direct pipe from runtime events to Ritesh's RL layer."""
    
    def __init__(self, env='dev'):
        self.env = env
        # Pass environment to RL layer for determinism control
        self.rl_layer = RLDecisionLayer(env=env)
        
    def pipe_runtime_event(self, event_data):
        """Pipe runtime event to RL with structured proof logging and validation."""
        
        # Strict validation BEFORE calling RL
        from core.runtime_event_validator import validate_and_log_payload
        from core.proof_logger import write_proof, ProofEvents
        
        is_valid, validated_payload, error_msg = validate_and_log_payload(event_data, "RL_INPUT")
        
        if not is_valid:
            # Log validation error
            print(f"VALIDATION ERROR: {error_msg}")
            
            # Return safe NOOP without calling RL
            from core.rl_orchestrator_safe import get_safe_executor
            safe_executor = get_safe_executor(self.env)
            noop_result = safe_executor.validate_and_execute(0, {})  # Action 0 = noop
            
            return {
                'rl_action': 0,
                'execution': noop_result,
                'validation_error': error_msg
            }
        
        # Structured proof logging - RL_CONSUME
        write_proof(ProofEvents.RL_CONSUME, {
            'env': self.env,
            'event_type': validated_payload.get('event_type'),
            'payload': validated_payload,
            'status': 'consumed'
        })
        
        # Log payload before RL (unchanged pass-through)
        from core.runtime_event_validator import RuntimeEventValidator
        RuntimeEventValidator.log_payload_integrity(validated_payload, "RL_CONSUME")
        
        # Get RL decision with UNCHANGED payload
        rl_action = self.rl_layer.process_state(validated_payload)
        
        # Structured proof logging - RL_DECISION
        write_proof(ProofEvents.RL_DECISION, {
            'env': self.env,
            'event_type': validated_payload.get('event_type'),
            'payload': validated_payload,
            'decision': rl_action,
            'status': 'decided'
        })
        
        # Safe execution validation
        from core.rl_orchestrator_safe import get_safe_executor
        safe_executor = get_safe_executor(self.env)
        
        # Validate and execute (or refuse)
        execution_result = safe_executor.validate_and_execute(rl_action, validated_payload)
        
        return {
            'rl_action': rl_action,
            'execution': execution_result
        }

# Global RL pipe instances per environment
_rl_pipes = {}

def get_rl_pipe(env='dev'):
    """Get RL pipe instance for specific environment."""
    global _rl_pipes
    if env not in _rl_pipes:
        _rl_pipes[env] = RuntimeRLPipe(env)
    return _rl_pipes[env]