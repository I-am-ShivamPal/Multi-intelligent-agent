#!/usr/bin/env python3
"""Cross-Environment Comparison Dashboard"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core.metrics_collector import get_metrics_collector

def render_cross_env_dashboard():
    """Render cross-environment comparison dashboard."""
    st.header("🌍 Cross-Environment Comparison")
    
    # Load metrics from all environments
    envs = ['dev', 'stage', 'prod']
    env_data = {}
    
    for env in envs:
        try:
            collector = get_metrics_collector(env)
            env_data[env] = collector.get_metrics_summary()
        except Exception as e:
            env_data[env] = {}
            st.warning(f"Could not load {env} metrics: {e}")
    
    # Environment Health Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Environment Health Overview")
        
        health_data = []
        for env in envs:
            data = env_data.get(env, {})
            health_data.append({
                'Environment': env.upper(),
                'Uptime %': data.get('uptime_percentage', 0),
                'Success Rate %': data.get('deployment_success_rate', 0) * 100,
                'Avg Latency (ms)': data.get('avg_latency', 0)
            })
        
        health_df = pd.DataFrame(health_data)
        st.dataframe(health_df, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Performance Comparison")
        
        if not health_df.empty:
            fig = px.bar(health_df, x='Environment', y=['Uptime %', 'Success Rate %'],
                        title="Uptime vs Success Rate by Environment",
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
    
    # Latency Comparison Chart
    st.subheader("⚡ Latency Comparison Across Environments")
    
    latency_data = []
    for env in envs:
        data = env_data.get(env, {})
        latency_data.append({
            'Environment': env.upper(),
            'Avg Latency': data.get('avg_latency', 0),
            'Max Latency': data.get('max_latency', 0),
            'Min Latency': data.get('min_latency', 0)
        })
    
    latency_df = pd.DataFrame(latency_data)
    
    if not latency_df.empty:
        fig_latency = px.line(latency_df, x='Environment', y=['Avg Latency', 'Max Latency'],
                             title="Latency Trends Across Environments",
                             markers=True)
        st.plotly_chart(fig_latency, use_container_width=True)
    
    # Environment Status Matrix
    st.subheader("🚦 Environment Status Matrix")
    
    status_cols = st.columns(3)
    
    for i, env in enumerate(envs):
        with status_cols[i]:
            data = env_data.get(env, {})
            uptime = data.get('uptime_percentage', 0)
            success_rate = data.get('deployment_success_rate', 0) * 100
            
            # Determine status color
            if uptime > 95 and success_rate > 90:
                status_color = "🟢"
                status_text = "HEALTHY"
            elif uptime > 85 and success_rate > 75:
                status_color = "🟡"
                status_text = "WARNING"
            else:
                status_color = "🔴"
                status_text = "CRITICAL"
            
            st.metric(
                f"{status_color} {env.upper()}",
                status_text,
                f"{uptime:.1f}% uptime"
            )
            
            with st.expander(f"📊 {env.upper()} Details"):
                st.write(f"**Deployment Success**: {success_rate:.1f}%")
                st.write(f"**Average Latency**: {data.get('avg_latency', 0):.0f}ms")
                st.write(f"**Total Events**: {data.get('total_events', 0)}")
                st.write(f"**Error Count**: {data.get('error_count', 0)}")
    
    # Cross-Environment Alerts
    st.subheader("⚠️ Cross-Environment Alerts")
    
    alerts = []
    for env in envs:
        data = env_data.get(env, {})
        uptime = data.get('uptime_percentage', 0)
        success_rate = data.get('deployment_success_rate', 0) * 100
        latency = data.get('avg_latency', 0)
        
        if uptime < 95:
            alerts.append(f"🔴 {env.upper()}: Low uptime ({uptime:.1f}%)")
        if success_rate < 90:
            alerts.append(f"🟡 {env.upper()}: Low success rate ({success_rate:.1f}%)")
        if latency > 15000:
            alerts.append(f"⚡ {env.upper()}: High latency ({latency:.0f}ms)")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ All environments operating within normal parameters")

if __name__ == "__main__":
    st.set_page_config(page_title="Cross-Environment Dashboard", layout="wide")
    render_cross_env_dashboard()