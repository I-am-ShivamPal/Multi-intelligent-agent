import json
import os
import numpy as np
from collections import defaultdict

class RLDecisionLayer:
    def __init__(self, state_space_size=100, action_space_size=10, learning_rate=0.1, discount_factor=0.9, epsilon=0.1, env='dev'):
        self.state_space_size = state_space_size
        self.action_space_size = action_space_size
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.env = env
        
        # Force determinism in STAGE environment
        if env == 'stage':
            self.epsilon = 0.0  # No exploration in stage
            np.random.seed(42)  # Fixed seed for deterministic behavior
        else:
            self.epsilon = epsilon
            
        self.q_table = defaultdict(lambda: np.zeros(action_space_size))
        self.summary_file = 'fusion_rl_summary.json'
        self.load_summary()

    def load_summary(self):
        if os.path.exists(self.summary_file):
            with open(self.summary_file, 'r') as f:
                data = json.load(f)
                self.q_table = defaultdict(lambda: np.zeros(self.action_space_size), data.get('q_table', {}))
                for k, v in self.q_table.items():
                    self.q_table[k] = np.array(v)

    def save_summary(self):
        data = {
            'q_table': {k: v.tolist() for k, v in self.q_table.items()},
            'last_updated': str(np.datetime64('now'))
        }
        with open(self.summary_file, 'w') as f:
            json.dump(data, f, indent=4)

    def get_state_key(self, state):
        # Convert state dict to a hashable key
        return str(sorted(state.items()))

    def process_state(self, rl_state):
        state_key = self.get_state_key(rl_state)
        
        # Force NOOP for false_alarm events (deterministic rule)
        if isinstance(rl_state, dict) and rl_state.get('event_type') == 'false_alarm':
            return 0  # NOOP action
        
        # STAGE environment: Force deterministic action selection
        if self.env == 'stage':
            # Use deterministic mapping based on state key hash
            import hashlib
            hash_obj = hashlib.md5(state_key.encode())
            hash_int = int(hash_obj.hexdigest(), 16)
            action = hash_int % self.action_space_size
            return int(action)
        
        # Normal epsilon-greedy for other environments
        if np.random.rand() < self.epsilon:
            action = int(np.random.randint(self.action_space_size))
        else:
            action = int(np.argmax(self.q_table[state_key]))
        return action
    
    def get_decision_with_metadata(self, rl_state):
        """
        Get decision with source metadata for orchestrator validation
        
        Returns:
            dict: Action decision with source tracking metadata
        """
        import datetime
        import uuid
        
        action = self.process_state(rl_state)
        
        return {
            'action': action,
            'source': 'rl_decision_layer',
            'decision_id': str(uuid.uuid4())[:8],
            'timestamp': datetime.datetime.now().isoformat(),
            'env': self.env,
            'state': rl_state,
        }

    def record_action_result(self, rl_state, action, reward, next_rl_state):
        state_key = self.get_state_key(rl_state)
        next_state_key = self.get_state_key(next_rl_state)
        
        old_value = self.q_table[state_key][action]
        next_max = np.max(self.q_table[next_state_key])
        new_value = old_value + self.learning_rate * (reward + self.discount_factor * next_max - old_value)
        self.q_table[state_key][action] = new_value
        
        self.save_summary()
        return new_value - old_value  # reward change

    def get_q_table_summary(self):
        return dict(self.q_table)
    