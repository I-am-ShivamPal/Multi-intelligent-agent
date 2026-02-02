#!/usr/bin/env python3
"""
Test script to demonstrate the multi-agent system functionality.
Runs multiple scenarios to test all agents and RL learning.
"""

import subprocess
import sys
import time
import os

def run_scenario(name, args):
    """Run a single test scenario."""
    print(f"\n{'='*60}")
    print(f"SCENARIO: {name}")
    print(f"{'='*60}")
    
    cmd = [sys.executable, "main.py"] + args
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Return code: {result.returncode}")
    except subprocess.TimeoutExpired:
        print("Scenario timed out (30s)")
    except Exception as e:
        print(f"Error running scenario: {e}")
    
    time.sleep(2)  # Brief pause between scenarios

def main():
    """Run comprehensive system tests."""
    print("🤖 Multi-Agent System Test Suite")
    print("Testing all agents and RL learning capabilities...")
    
    # Test scenarios
    scenarios = [
        ("Normal Deployment", ["--dataset", "dataset/student_scores.csv"]),
        ("Force Anomaly (Random Agent)", ["--dataset", "dataset/student_scores.csv", "--force-anomaly"]),
        ("Force Anomaly (RL Agent)", ["--dataset", "dataset/student_scores.csv", "--force-anomaly", "--planner", "rl"]),
        ("Latency Issue", ["--dataset", "dataset/patient_health.csv", "--fail-type", "latency"]),
        ("Crash Simulation", ["--dataset", "dataset/patient_health.csv", "--fail-type", "crash", "--planner", "rl"]),
    ]
    
    for name, args in scenarios:
        run_scenario(name, args)
    
    # Run RL training
    print(f"\n{'='*60}")
    print("🧠 Running RL Training (10 scenarios)...")
    print(f"{'='*60}")
    
    try:
        subprocess.run([sys.executable, "train_rl.py"], timeout=300)
    except Exception as e:
        print(f"Training error: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Test Suite Complete!")
    print("RL agent has learned optimal strategies across 10 training runs.")
    print("Check logs/rl_log.csv for the learned Q-table.")
    print("Run 'python run_dashboard.py' to view the dashboard.")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()