#!/usr/bin/env python3
"""Launch enhanced InsightFlow dashboard."""

import subprocess
import sys
import os

def main():
    # Ensure required directories exist
    os.makedirs("insightflow", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # Initialize telemetry file if not exists
    if not os.path.exists("insightflow/telemetry.json"):
        with open("insightflow/telemetry.json", 'w') as f:
            f.write("[]")
    
    print("🚀 Starting InsightFlow Dashboard...")
    print("📊 Real-time agent monitoring enabled")
    print("🔄 Auto-refresh every 5 seconds")
    print("💡 Toggle between User/Developer modes")
    print("🌐 Dashboard will be available at: http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/dashboard.py",
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")
        print("💡 Try running: streamlit run dashboard/dashboard.py")

if __name__ == "__main__":
    main()