#!/usr/bin/env python3
"""Test Redis Demo Behavior"""

import unittest
from unittest.mock import patch, MagicMock
from core.redis_demo_behavior import get_redis_bus_demo_safe, RedisUnavailableError, RedisStub, validate_redis_for_demo

class TestRedisDemoBehavior(unittest.TestCase):
    
    @patch('core.redis_demo_behavior.get_redis_bus')
    def test_redis_available_returns_real_bus(self, mock_get_redis):
        """Test that real Redis bus is returned when available."""
        mock_bus = MagicMock()
        mock_get_redis.return_value = mock_bus
        
        result = get_redis_bus_demo_safe('dev', use_stub=False)
        
        self.assertEqual(result, mock_bus)
        mock_bus.publish.assert_called_once_with("test.connection", {"test": True})
    
    @patch('core.redis_demo_behavior.get_redis_bus')
    def test_redis_unavailable_with_stub_returns_stub(self, mock_get_redis):
        """Test that stub is returned when Redis unavailable and stub requested."""
        mock_get_redis.side_effect = Exception("Redis connection failed")
        
        result = get_redis_bus_demo_safe('dev', use_stub=True)
        
        self.assertIsInstance(result, RedisStub)
        self.assertEqual(result.env, 'dev')
    
    @patch('core.redis_demo_behavior.get_redis_bus')
    def test_redis_unavailable_no_stub_raises_error(self, mock_get_redis):
        """Test that error is raised when Redis unavailable and no stub requested."""
        mock_get_redis.side_effect = Exception("Redis connection failed")
        
        with self.assertRaises(RedisUnavailableError) as cm:
            get_redis_bus_demo_safe('dev', use_stub=False)
        
        self.assertIn("Redis unavailable", str(cm.exception))
    
    def test_redis_stub_stores_messages(self):
        """Test that Redis stub stores messages locally."""
        stub = RedisStub('test')
        
        stub.publish('test.channel', {'data': 'test'})
        
        messages = stub.get_messages()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]['channel'], 'test.channel')
        self.assertEqual(messages[0]['message']['data'], 'test')
    
    @patch('core.redis_demo_behavior.get_redis_bus_demo_safe')
    def test_validate_redis_connected(self, mock_get_redis):
        """Test Redis validation when connected."""
        mock_get_redis.return_value = MagicMock()
        
        result = validate_redis_for_demo('dev')
        
        self.assertEqual(result['status'], 'connected')
        self.assertEqual(result['type'], 'redis')
    
    @patch('core.redis_demo_behavior.get_redis_bus_demo_safe')
    def test_validate_redis_unavailable(self, mock_get_redis):
        """Test Redis validation when unavailable."""
        mock_get_redis.side_effect = RedisUnavailableError("Redis unavailable")
        
        result = validate_redis_for_demo('dev')
        
        self.assertEqual(result['status'], 'unavailable')
        self.assertIn('no stub configured', result['message'])

if __name__ == '__main__':
    unittest.main()