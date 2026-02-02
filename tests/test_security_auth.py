import unittest
from unittest.mock import patch, MagicMock
import time
from security.auth import TokenAuth, get_auth, verify_token, require_auth

class TestSecurityAuth(unittest.TestCase):
    
    def setUp(self):
        self.auth = TokenAuth(secret_key='test-secret-key')
    
    @patch('time.time')
    def test_verify_token_valid_token(self, mock_time):
        # Fix: Use consistent time for both generation and verification
        current_time = 1000000.0
        mock_time.return_value = current_time
        
        token = self.auth.generate_token('test_user', expires_in=3600)
        
        # Keep same time for verification (token not expired)
        mock_time.return_value = current_time + 1800  # 30 minutes later
        
        result = self.auth.verify_token(token)
        self.assertTrue(result['valid'])
        self.assertEqual(result['payload']['user_id'], 'test_user')
    
    @patch('time.time')
    def test_require_token_decorator_valid(self, mock_time):
        # Fix: Use consistent time
        current_time = 1000000.0
        mock_time.return_value = current_time
        
        token = self.auth.generate_token('test_user', expires_in=3600)
        
        @self.auth.require_token
        def protected_func(token=None):
            return "success"
        
        # Keep same time for verification
        mock_time.return_value = current_time + 1800
        
        result = protected_func(token=token)
        self.assertEqual(result, "success")

if __name__ == '__main__':
    unittest.main()
