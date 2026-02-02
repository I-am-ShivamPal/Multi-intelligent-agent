#!/usr/bin/env python3
"""
Simple web dashboard for CI/CD monitoring system.
Optimized for deployment on Render and other cloud platforms.
"""

import streamlit as st
import pandas as pd
import os
import plotly.express as px
import datetime
import json

# Page config
st.set_page_config(
    page_title="CI/CD Monitor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Simple data loader
@st.cache_data(ttl=10)
def load_simple_data():
    data = {}
    
    # Core files only
    files = {
        "deployments": os.path.join("logs", r"deployment_log.csv"),
        "healing": os.path.join("logs", r"healing_log.csv"), 
        "issues": os.path.join("logs", r"issue_log.csv"),
        "uptime": os.path.join("logs", r"uptime_log.csv")
    }
    
    for key, path in files.items():
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                data[key] = df
            except:
                data[key] = pd.DataFrame()
        else:
            data[key] = pd.DataFrame()
    
    return data

# Load data
data = load_simple_data()
deployments = data["deployments"]
healing = data["healing"]
issues = data["issues"]
uptime = data["uptime"]

# Header
st.title("🤖 CI/CD Multi-Agent System")
st.markdown("**Real-time monitoring dashboard for intelligent deployment automation**")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    deploy_count = len(deployments) if not deployments.empty else 0
    st.metric("Total Deployments", deploy_count)

with col2:
    issue_count = len(issues) if not issues.empty else 0
    st.metric("Issues Detected", issue_count)

with col3:
    heal_count = len(healing) if not healing.empty else 0
    st.metric("Auto Heals", heal_count)

with col4:
    if not healing.empty:
        success_rate = (healing['status'] == 'success').mean() * 100
        st.metric("Heal Success", f"{success_rate:.0f}%")
    else:
        st.metric("Heal Success", "N/A")

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📊 System Overview", "🔧 Agent Activity", "📈 Performance"])

with tab1:
    st.header("System Status")
    
    # System health
    if not uptime.empty:
        up_pct = (uptime['status'] == 'UP').mean() * 100 if 'status' in uptime.columns else 100
        st.success(f"System Uptime: {up_pct:.1f}%")
    else:
        st.info("Uptime data not available")
    
    # Recent events
    st.subheader("Recent Activity")
    
    recent_events = []
    
    if not deployments.empty:
        for _, row in deployments.tail(3).iterrows():
            recent_events.append({
                'Time': row.get('timestamp', 'Unknown'),
                'Type': 'Deployment',
                'Status': row.get('status', 'Unknown'),
                'Details': row.get('details', 'N/A')
            })
    
    if not issues.empty:
        for _, row in issues.tail(3).iterrows():
            recent_events.append({
                'Time': row.get('timestamp', 'Unknown'),
                'Type': 'Issue',
                'Status': row.get('failure_state', 'Unknown'),
                'Details': row.get('reason', 'N/A')
            })
    
    if recent_events:
        events_df = pd.DataFrame(recent_events)
        events_df = events_df.sort_values('Time', ascending=False)
        st.dataframe(events_df, use_container_width=True)
    else:
        st.info("No recent events")

with tab2:
    st.header("Agent Intelligence")
    
    # Healing performance
    if not healing.empty:
        st.subheader("Auto-Heal Agent")
        
        success_count = (healing['status'] == 'success').sum()
        total_count = len(healing)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Healing Attempts", total_count)
        with col2:
            st.metric("Success Rate", f"{success_count/total_count*100:.1f}%")
        
        # Success pie chart
        if total_count > 0:
            fig = px.pie(
                names=['Success', 'Failed'],
                values=[success_count, total_count - success_count],
                title="Healing Outcomes"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No healing data available")
    
    # Issue detection
    if not issues.empty:
        st.subheader("Issue Detection")
        
        if 'failure_state' in issues.columns:
            issue_types = issues['failure_state'].value_counts()
            fig = px.bar(
                x=issue_types.index,
                y=issue_types.values,
                title="Issue Types Detected"
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No issues detected")

with tab3:
    st.header("Performance Trends")
    
    # Deployment timeline
    if not deployments.empty and 'timestamp' in deployments.columns:
        st.subheader("Deployment Timeline")
        
        # Group by date
        deployments['date'] = deployments['timestamp'].dt.date
        daily_deploys = deployments.groupby('date').size().reset_index(name='count')
        
        fig = px.line(
            daily_deploys,
            x='date',
            y='count',
            title="Daily Deployments",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No deployment timeline data")
    
    # Healing trends
    if not healing.empty and len(healing) > 1:
        st.subheader("Healing Success Over Time")
        
        healing['success'] = (healing['status'] == 'success').astype(int)
        healing['cumulative_success'] = healing['success'].expanding().mean() * 100
        
        fig = px.line(
            healing.reset_index(),
            x='index',
            y='cumulative_success',
            title="Success Rate Improvement",
            markers=True
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient healing data for trends")

# Footer
st.markdown("---")
st.markdown("**Multi-Agent CI/CD System** | Intelligent deployment automation with self-healing capabilities")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()