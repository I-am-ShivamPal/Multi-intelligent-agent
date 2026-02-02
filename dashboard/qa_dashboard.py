#!/usr/bin/env python3
"""Simplified QA Dashboard - Clear view for QA results."""

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
import glob

def load_qa_summaries():
    """Load all QA summary files."""
    pattern = os.path.join("logs", r"qa_summary_*.csv")
    files = glob.glob(pattern)
    
    if not files:
        return pd.DataFrame()
    
    summaries = []
    for file in files:
        try:
            df = pd.read_csv(file)
            summaries.append(df)
        except:
            continue
    
    if summaries:
        return pd.concat(summaries, ignore_index=True)
    return pd.DataFrame()

def main():
    st.set_page_config(page_title="QA Dashboard", page_icon="🧪", layout="wide")
    
    st.title("🧪 QA Dashboard")
    st.markdown("**Clear QA summary view for Vinayak's test results**")
    
    # Load QA data
    qa_data = load_qa_summaries()
    
    if qa_data.empty:
        st.warning("No QA data found. Run `python run_qa.py` to generate test results.")
        st.code("python run_qa.py", language="bash")
        return
    
    # Latest results
    latest = qa_data.iloc[-1] if not qa_data.empty else None
    
    if latest is not None:
        st.subheader("📊 Latest QA Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = "🟢" if latest['system_status'] == 'STABLE' else "🟡"
            st.metric("System Status", f"{status_color} {latest['system_status']}")
        
        with col2:
            st.metric("Test Pass Rate", f"{latest['pass_rate_pct']:.1f}%", 
                     delta=f"{latest['passed_tests']}/{latest['total_tests']} passed")
        
        with col3:
            st.metric("System Uptime", f"{latest['uptime_pct']:.1f}%")
        
        with col4:
            st.metric("Issues/Heals", f"{latest['total_issues']}/{latest['total_heals']}")
    
    # Trend chart
    if len(qa_data) > 1:
        st.subheader("📈 QA Trends")
        
        qa_data['date'] = pd.to_datetime(qa_data['date'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pass = px.line(qa_data, x='date', y='pass_rate_pct', 
                              title="Test Pass Rate Over Time",
                              labels={'pass_rate_pct': 'Pass Rate %', 'date': 'Date'})
            fig_pass.add_hline(y=80, line_dash="dash", line_color="red", 
                              annotation_text="Target: 80%")
            st.plotly_chart(fig_pass, use_container_width=True)
        
        with col2:
            fig_uptime = px.line(qa_data, x='date', y='uptime_pct',
                               title="System Uptime Over Time", 
                               labels={'uptime_pct': 'Uptime %', 'date': 'Date'})
            fig_uptime.add_hline(y=95, line_dash="dash", line_color="red",
                                annotation_text="SLA: 95%")
            st.plotly_chart(fig_uptime, use_container_width=True)
    
    # QA Summary Table
    st.subheader("📋 QA History")
    st.dataframe(qa_data.sort_values('date', ascending=False), use_container_width=True)
    
    # Quick Actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Run QA Tests", type="primary"):
            with st.spinner("Running QA tests..."):
                import subprocess
                try:
                    result = subprocess.run(["python", "run_qa.py"], 
                                          capture_output=True, text=True, timeout=60)
                    if result.returncode == 0:
                        st.success("✅ QA tests completed successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ QA tests failed: {result.stderr}")
                except Exception as e:
                    st.error(f"❌ Error running tests: {e}")
    
    with col2:
        if st.button("📊 View Main Dashboard"):
            st.switch_page("dashboard/dashboard.py")
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()

if __name__ == "__main__":
    main()