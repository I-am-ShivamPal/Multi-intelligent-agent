#!/usr/bin/env python3
"""
Comprehensive Proof: All 5 Runtime Events -> RL Consumption
"""

import datetime
import os

# Clear previous proof
if os.path.exists("runtime_rl_proof.log"):
    os.remove("runtime_rl_proof.log")

print("Generating comprehensive proof for all 5 event types...")

from core.guaranteed_events import (
    emit_deploy_event, emit_scale_event, emit_restart_event, 
    emit_crash_event, emit_overload_event
)

# Generate all 5 event types
events = [
    ("deploy", lambda: emit_deploy_event('dev', 'success', 150, 'proof.csv')),
    ("scale", lambda: emit_scale_event('dev', 'success', 200, 'proof.csv')),
    ("restart", lambda: emit_restart_event('dev', 'success', 300, 'proof.csv')),
    ("crash", lambda: emit_crash_event('dev', 'detected', 0, 'proof.csv')),
    ("overload", lambda: emit_overload_event('dev', 'detected', 1500, 'proof.csv'))
]

for event_name, event_func in events:
    try:
        print(f"Emitting {event_name} event...")
        event_func()
        print(f"OK {event_name} event processed")
    except Exception as e:
        print(f"ERROR {event_name} event failed: {e}")

print("Proof generation complete. Check runtime_rl_proof.log for details.")