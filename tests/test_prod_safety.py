#!/usr/bin/env python3
"""Test Production Safety Guards"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import unittest.mock
from core.prod_safety import validate_prod_action, ProductionSafetyError, is_action_safe_for_prod

class TestProductionSafety(unittest.TestCase):
    
    def test_dev_allows_all_actions(self):
        """Dev environment should allow all actions."""
        for action in ['scale_up', 'scale_down', 'restore_previous_version', 'adjust_thresholds']:
            self.assertTrue(validate_prod_action(action, 'dev'))
    
    def test_prod_blocks_risky_actions(self):
        """Prod should block risky actions and emit proper refusal."""
        from agents.auto_heal_agent import AutoHealAgent
        import tempfile
        import os
        
        # Create temp log file
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_file.close()
        
        try:
            # Create agent in prod environment
            agent = AutoHealAgent(temp_file.name, env='prod')
            agent.logger = unittest.mock.MagicMock()
            agent.redis_bus = unittest.mock.MagicMock()
            
            # Test blocked action
            status, response_time, heal_type, strategy = agent.execute_action('restore_previous_version', 'test.csv')
            
            # Verify deterministic response
            self.assertEqual(status, 'refused')
            self.assertEqual(response_time, 0)
            self.assertEqual(heal_type, 'prod_safety_block')
            self.assertEqual(strategy, 'restore_previous_version')
            
            # Verify refusal event was emitted
            agent.redis_bus.publish.assert_called_with("action.refused", unittest.mock.ANY)
            
        finally:
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
    
    def test_prod_allows_safe_actions(self):
        """Prod should allow safe actions."""
        safe_actions = ['noop', 'restart', 'retry_deployment']
        
        for action in safe_actions:
            self.assertTrue(validate_prod_action(action, 'prod'))
    
    def test_is_action_safe_for_prod(self):
        """Test safe action checker."""
        self.assertTrue(is_action_safe_for_prod('restart'))
        self.assertFalse(is_action_safe_for_prod('scale_up'))

if __name__ == '__main__':
    unittest.main()