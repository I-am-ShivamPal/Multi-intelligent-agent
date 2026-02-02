#!/usr/bin/env python3
"""Launch simple web dashboard for cloud deployment."""

import subprocess
import sys
import os

def main():
    # Ensure required directories exist
    os.makedirs("logs", exist_ok=True)
    
    print("🚀 Starting Web Dashboard...")
    print("🌐 Optimized for cloud deployment")
    print("📊 Simple monitoring interface")
    print("🔗 Dashboard will be available at: http://localhost:8501")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "web_dashboard.py",
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try: streamlit run web_dashboard.py")

if __name__ == "__main__":
    main()