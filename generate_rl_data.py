#!/usr/bin/env python3
"""Generate sample RL training data for dashboard visualization"""
import pandas as pd
import numpy as np
import os

def generate_qtable_data():
    """Generate Q-table with sample training data."""
    states = ['deployment_failure', 'latency_issue', 'anomaly_score', 'anomaly_health']
    actions = ['retry_deployment', 'restore_previous_version', 'adjust_thresholds']
    
    # Generate realistic Q-values
    qtable = {}
    for state in states:
        qtable[state] = {}
        for action in actions:
            # Simulate learned Q-values
            if state == 'deployment_failure' and action == 'retry_deployment':
                qtable[state][action] = np.random.uniform(0.7, 0.9)
            elif state == 'latency_issue' and action == 'adjust_thresholds':
                qtable[state][action] = np.random.uniform(0.6, 0.8)
            elif state == 'anomaly_score' and action == 'restore_previous_version':
                qtable[state][action] = np.random.uniform(0.5, 0.7)
            else:
                qtable[state][action] = np.random.uniform(0.1, 0.5)
    
    # Save to CSV
    df = pd.DataFrame(qtable).T
    df.to_csv('logs/dev/rl_log.csv')
    print(f"✅ Generated Q-table: logs/dev/rl_log.csv")
    
    return df

def generate_reward_data():
    """Generate reward trends data."""
    episodes = 50
    
    data = []
    cumulative_reward = 0
    
    for episode in range(1, episodes + 1):
        # Simulate improving rewards over time
        base_reward = np.random.uniform(-1, 1)
        learning_bonus = episode / episodes * 0.5
        reward = base_reward + learning_bonus
        cumulative_reward += reward
        
        data.append({
            'episode': episode,
            'reward': reward,
            'cumulative_reward': cumulative_reward,
            'avg_reward': cumulative_reward / episode
        })
    
    df = pd.DataFrame(data)
    df.to_csv('logs/dev/rl_performance_log.csv', index=False)
    print(f"✅ Generated reward data: logs/dev/rl_performance_log.csv")
    
    return df

if __name__ == "__main__":
    print("🤖 Generating RL Training Data")
    print("=" * 40)
    
    # Ensure directories exist
    os.makedirs('logs/dev', exist_ok=True)
    os.makedirs('logs/stage', exist_ok=True)
    os.makedirs('logs/prod', exist_ok=True)
    
    # Generate data
    qtable = generate_qtable_data()
    rewards = generate_reward_data()
    
    print("\n📊 Q-Table Sample:")
    print(qtable.head())
    
    print("\n📈 Reward Trends Sample:")
    print(rewards.tail())
    
    print("\n🎉 RL data generated successfully!")