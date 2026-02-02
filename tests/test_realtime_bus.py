import unittest
import tempfile
import os
from core.realtime_bus import RealtimeBus

class TestRealtimeBus(unittest.TestCase):
    def setUp(self):
        self.bus = RealtimeBus()
    
    def test_create_queue(self):
        self.bus.create_queue("test_topic")
        self.assertIn("test_topic", self.bus.queues)
    
    def test_publish_message(self):
        message = {"type": "test", "data": "hello"}
        self.bus.publish("test_topic", message)
        self.assertEqual(self.bus.message_count, 1)
    
    def test_subscribe_callback(self):
        received_messages = []
        
        def callback(message):
            received_messages.append(message)
        
        self.bus.subscribe("test_topic", callback)
        self.bus.publish("test_topic", {"type": "test"})
        
        self.assertEqual(len(received_messages), 1)
    
    def test_get_stats(self):
        self.bus.publish("test_topic", {"test": "data"})
        stats = self.bus.get_stats()
        
        self.assertIn("total_messages", stats)
        self.assertGreater(stats["total_messages"], 0)

if __name__ == "__main__":
    unittest.main()