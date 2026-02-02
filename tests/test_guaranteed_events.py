#!/usr/bin/env python3
"""Test Guaranteed Event Emission"""

import unittest
import tempfile
import os
import shutil
from unittest.mock import MagicMock, patch
from core.guaranteed_events import GuaranteedEventEmitter, EventEmissionError

class TestGuaranteedEvents(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.redis_bus = MagicMock()
        self.metrics = MagicMock()
        self.emitter = GuaranteedEventEmitter('test', self.redis_bus, self.metrics, self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_successful_emission_all_destinations(self):
        """Test successful emission to all destinations."""
        self.emitter.emit_runtime_event("deploy", "success", 1200, dataset="test.csv")
        
        # Verify Redis emission
        self.redis_bus.publish.assert_called_once()
        
        # Verify CSV log created
        csv_file = os.path.join(self.temp_dir, "deploy_runtime_events.csv")
        self.assertTrue(os.path.exists(csv_file))
        
        # Verify metrics emission
        self.metrics.record_deploy_metric.assert_called_once()
    
    def test_redis_failure_raises_error(self):
        """Test that Redis failure raises EventEmissionError."""
        self.redis_bus.publish.side_effect = Exception("Redis connection failed")
        
        with self.assertRaises(EventEmissionError) as cm:
            self.emitter.emit_runtime_event("deploy", "success", 1200)
        
        self.assertIn("Redis emission failed", str(cm.exception))
    
    def test_csv_failure_raises_error(self):
        """Test that CSV failure raises EventEmissionError."""
        # Make directory read-only to cause CSV write failure
        os.chmod(self.temp_dir, 0o444)
        
        try:
            with self.assertRaises(EventEmissionError) as cm:
                self.emitter.emit_runtime_event("deploy", "success", 1200)
            
            self.assertIn("CSV emission failed", str(cm.exception))
        finally:
            os.chmod(self.temp_dir, 0o755)  # Restore permissions
    
    def test_metrics_failure_raises_error(self):
        """Test that metrics failure raises EventEmissionError."""
        self.metrics.record_deploy_metric.side_effect = Exception("Metrics system down")
        
        with self.assertRaises(EventEmissionError) as cm:
            self.emitter.emit_runtime_event("deploy", "success", 1200)
        
        self.assertIn("Metrics emission failed", str(cm.exception))
    
    def test_no_silent_failures(self):
        """Test that ANY failure prevents silent operation."""
        # Simulate partial failure (Redis works, CSV fails, Metrics works)
        os.chmod(self.temp_dir, 0o444)  # Make CSV fail
        
        try:
            with self.assertRaises(EventEmissionError):
                self.emitter.emit_runtime_event("deploy", "success", 1200)
            
            # Even though Redis and Metrics would work, the whole operation fails
            self.redis_bus.publish.assert_called_once()  # Redis was attempted
            
        finally:
            os.chmod(self.temp_dir, 0o755)

if __name__ == '__main__':
    unittest.main()