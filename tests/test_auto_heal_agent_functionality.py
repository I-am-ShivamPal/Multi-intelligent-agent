import unittest
from unittest.mock import patch, MagicMock, PropertyMock
import tempfile
import os

class TestAutoHealAgent(unittest.TestCase):
    
    @patch('agents.auto_heal_agent.get_redis_bus')
    @patch('agents.auto_heal_agent.BaseAgent.__init__')
    def setUp(self, mock_base_init, mock_redis):
        # Fix: Mock BaseAgent initialization to prevent logger attribute error
        mock_base_init.return_value = None
        mock_redis.return_value = MagicMock()
        
        from agents.auto_heal_agent import AutoHealAgent
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.close()
        
        self.agent = AutoHealAgent(self.temp_file.name, env='dev')
        
        # Fix: Manually set logger attribute
        self.agent.logger = MagicMock()
        self.agent.redis_bus = mock_redis.return_value
    
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_agent_initialization(self):
        self.assertEqual(self.agent.env, 'dev')
        self.assertEqual(len(self.agent.strategies), 3)
    
    @patch('agents.auto_heal_agent.random.choice')
    def test_attempt_healing_random_strategy(self, mock_choice):
        mock_choice.return_value = 'retry_deployment'
        self.agent._retry_deployment = MagicMock(return_value=('success', 100))
        
        status, response_time, heal_type, strategy = self.agent.attempt_healing('failed', 'test.csv')
        
        self.assertEqual(strategy, 'retry_deployment')
        self.assertEqual(status, 'success')
    
    def test_execute_action_retry_deployment(self):
        self.agent._retry_deployment = MagicMock(return_value=('success', 150))
        
        status, response_time, heal_type, strategy = self.agent.execute_action('retry_deployment', 'test.csv')
        
        self.assertEqual(status, 'success')
        self.assertEqual(heal_type, 'heal_retry')
    
    def test_execute_action_adjust_thresholds(self):
        status, response_time, heal_type, strategy = self.agent.execute_action('adjust_thresholds', 'test.csv')
        
        self.assertEqual(status, 'success')
        self.assertEqual(heal_type, 'heal_adjust')
    
    def test_execute_action_restore_previous_version(self):
        self.agent._restore_previous_version = MagicMock(return_value=('success', 200))
        
        status, response_time, heal_type, strategy = self.agent.execute_action('restore_previous_version', 'test.csv')
        
        self.assertEqual(status, 'success')
        self.assertEqual(heal_type, 'heal_restore')
    
    def test_execute_action_unknown_strategy(self):
        status, response_time, heal_type, strategy = self.agent.execute_action('unknown_strategy', 'test.csv')
        
        self.assertEqual(status, 'failure')
        self.assertEqual(heal_type, 'unknown_strategy')
    
    def test_get_log_headers(self):
        headers = self.agent.get_log_headers()
        
        self.assertIn('timestamp', headers)
        self.assertIn('strategy', headers)
        self.assertIn('status', headers)

if __name__ == '__main__':
    unittest.main()
