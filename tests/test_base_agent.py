import unittest
import tempfile
import os
import pandas as pd
from core.base_agent import BaseAgent

class TestAgent(BaseAgent):
    def get_log_headers(self):
        return ["timestamp", "test_field"]
    
    def run(self):
        pass

class TestBaseAgent(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.csv")
        self.agent = TestAgent(self.log_file)
    
    def test_log_initialization(self):
        self.assertTrue(os.path.exists(self.log_file))
        df = pd.read_csv(self.log_file)
        self.assertEqual(list(df.columns), ["timestamp", "test_field"])
    
    def test_log_entry(self):
        self.agent._log_entry({"test_field": "test_value"})
        df = pd.read_csv(self.log_file)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]["test_field"], "test_value")
    
    def test_safe_read_csv(self):
        df = self.agent._safe_read_csv("nonexistent.csv")
        self.assertTrue(df.empty)
        
        # Add data to log file first
        self.agent._log_entry({"test_field": "test_value"})
        df = self.agent._safe_read_csv(self.log_file)
        self.assertFalse(df.empty)

if __name__ == "__main__":
    unittest.main()