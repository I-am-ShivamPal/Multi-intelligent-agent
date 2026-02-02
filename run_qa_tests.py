#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vinayak's QA Flow: Run tests and view results"""

import os
from datetime import datetime

print("Running QA Tests...\n")

tests = []

# Test 1: Data files
print("[1/3] Checking data files...")
try:
    import pandas as pd
    df1 = pd.read_csv('dataset/student.csv')
    df2 = pd.read_csv('dataset/patient.csv')
    tests.append(("Data Files", "PASS", f"{len(df1)} students, {len(df2)} patients"))
except Exception as e:
    tests.append(("Data Files", "FAIL", str(e)))

# Test 2: Dependencies
print("[2/3] Checking dependencies...")
try:
    import streamlit, plotly
    tests.append(("Dependencies", "PASS", "streamlit, plotly"))
except:
    tests.append(("Dependencies", "FAIL", "Missing packages"))

# Test 3: Dashboards
print("[3/3] Checking dashboards...")
dashboards = ['dashboard/student_viz.py', 'dashboard/patient_viz.py']
exists = all(os.path.exists(d) for d in dashboards)
tests.append(("Dashboards", "PASS" if exists else "FAIL", f"{len(dashboards)} files"))

# Results
print("\n" + "="*60)
print("QA TEST RESULTS")
print("="*60)
for name, status, info in tests:
    symbol = "[+]" if status == "PASS" else "[X]"
    print(f"{symbol} {status} - {name}: {info}")
print("="*60)
passed = sum(1 for t in tests if t[1] == "PASS")
print(f"Summary: {passed}/{len(tests)} tests passed ({passed*100//len(tests)}%)")
print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*60)
