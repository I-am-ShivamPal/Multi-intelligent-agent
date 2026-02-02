#!/usr/bin/env python3
"""
Demo Utilities - Clean Output Formatting

Provides consistent, readable output formatting for demo scripts.
"""

import datetime
from typing import Optional

class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'

def get_timestamp() -> str:
    """Get formatted timestamp."""
    return datetime.datetime.now().strftime("%H:%M:%S")

def print_banner(title: str):
    """Print demo banner."""
    width = 79
    print("\n" + "=" * width)
    print(f"{title:^{width}}")
    print("=" * width)
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print(f"Environment: stage")
    print()

def print_step(step_num: int, title: str, emoji: str = "🚀"):
    """Print formatted step header."""
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] {emoji} STEP {step_num}: {title}")

def print_substep(title: str, emoji: str = "→"):
    """Print substep."""
    print(f"           {emoji} {title}")

def print_success(message: str):
    """Print success message."""
    print(f"           ✅ {message}")

def print_info(message: str):
    """Print info message."""
    print(f"           ℹ️  {message}")

def print_warning(message: str):
    """Print warning message."""
    print(f"           ⚠️  {message}")

def print_failure(message: str):
    """Print failure message."""
    print(f"           ❌ {message}")

def print_separator(char: str = "-", width: int = 79):
    """Print visual separator."""
    print(char * width)

def print_summary_header():
    """Print summary report header."""
    print_separator("=")
    print(f"{'DEMO SUMMARY':^79}")
    print_separator("=")

def print_scenario(scenario_name: str, description: str):
    """Print scenario header."""
    print(f"\n           {Colors.BOLD}{scenario_name}{Colors.RESET}")
    print(f"           {description}")

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    else:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"

def print_proof_summary(proof_log_path: str):
    """Print proof log summary."""
    import os
    import json
    
    if not os.path.exists(proof_log_path):
        print_warning(f"Proof log not found: {proof_log_path}")
        return
    
    try:
        with open(proof_log_path, 'r') as f:
            events = [json.loads(line.strip()) for line in f if line.strip()]
        
        event_types = {}
        for event in events:
            event_name = event.get('event_name', 'unknown')
            event_types[event_name] = event_types.get(event_name, 0) + 1
        
        print(f"\nProof Events Logged: {len(events)}")
        print(f"Proof Log: {proof_log_path}")
        
        if event_types:
            print("\nEvent Breakdown:")
            for event_name, count in sorted(event_types.items()):
                print(f"  • {event_name}: {count}")
    
    except Exception as e:
        print_warning(f"Could not read proof log: {e}")
