#!/usr/bin/env python3
"""App-Centric Dashboard - Onboarded Apps View"""
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_onboarded_apps():
    """Load all onboarded apps from registry."""
    registry_path = 'apps/registry'
    apps = []
    
    if os.path.exists(registry_path):
        for file in os.listdir(registry_path):
            if file.endswith('.json'):
                with open(os.path.join(registry_path, file)) as f:
                    apps.append(json.load(f))
    
    return apps

def render_apps_overview():
    """Render apps overview section."""
    st.header("📱 Onboarded Applications")
    
    apps = load_onboarded_apps()
    
    if not apps:
        st.warning("No apps onboarded yet. Use `python apps/onboard_app.py` to onboard apps.")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Apps", len(apps))
    with col2:
        backend_count = sum(1 for app in apps if app['type'] == 'backend')
        st.metric("Backend Apps", backend_count)
    with col3:
        frontend_count = sum(1 for app in apps if app['type'] == 'frontend')
        st.metric("Frontend Apps", frontend_count)
    
    # Apps table
    st.subheader("Apps Registry")
    
    apps_data = []
    for app in apps:
        apps_data.append({
            'Name': app['name'],
            'Type': app['type'],
            'Port': app.get('port', 'N/A'),
            'Environments': ', '.join(app['environments']),
            'Onboarded': app.get('onboarded_at', 'N/A')[:10]
        })
    
    df = pd.DataFrame(apps_data)
    st.dataframe(df, use_container_width=True)

def render_app_details(app_name):
    """Render detailed view for selected app."""
    st.header(f"📦 {app_name} Details")
    
    # Load app spec
    spec_file = f'apps/registry/{app_name}.json'
    if not os.path.exists(spec_file):
        st.error(f"App spec not found: {spec_file}")
        return
    
    with open(spec_file) as f:
        app = json.load(f)
    
    # App info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Type", app['type'])
    with col2:
        st.metric("Port", app.get('port', 'N/A'))
    with col3:
        st.metric("Min Replicas", app.get('scaling', {}).get('min_replicas', 1))
    with col4:
        st.metric("Max Replicas", app.get('scaling', {}).get('max_replicas', 3))
    
    # Deployment history per environment
    st.subheader("🚀 Deployment History")
    
    for env in ['dev', 'stage', 'prod']:
        with st.expander(f"{env.upper()} Environment"):
            log_file = f'logs/{env}/{app_name}_deployment_log.csv'
            
            if os.path.exists(log_file):
                df = pd.read_csv(log_file)
                
                if not df.empty:
                    # Show last N deploys
                    st.write(f"**Last 5 Deployments:**")
                    recent = df.tail(5)
                    st.dataframe(recent, use_container_width=True)
                    
                    # Deployment stats
                    total = len(df)
                    success = (df['status'] == 'success').sum()
                    success_rate = (success / total * 100) if total > 0 else 0
                    avg_time = df['response_time_ms'].mean()
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Total Deploys", total)
                    with col_b:
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    with col_c:
                        st.metric("Avg Time", f"{avg_time:.0f}ms")
                else:
                    st.info("No deployments yet")
            else:
                st.info(f"No deployment log for {env}")
    
    # Health metrics
    st.subheader("💓 Health Metrics")
    
    for env in ['dev', 'stage', 'prod']:
        health_file = f'logs/{env}/{app_name}_health_log.csv'
        
        if os.path.exists(health_file):
            df = pd.read_csv(health_file)
            
            if not df.empty:
                latest = df.iloc[-1]
                
                col_h1, col_h2, col_h3, col_h4 = st.columns(4)
                
                with col_h1:
                    st.metric(f"{env.upper()}", "Healthy" if latest['healthy'] else "Unhealthy")
                with col_h2:
                    st.metric("Workers", latest['workers'])
                with col_h3:
                    st.metric("Last Check", latest['timestamp'][:19])
                with col_h4:
                    uptime = (df['healthy'].sum() / len(df) * 100) if len(df) > 0 else 0
                    st.metric("Uptime", f"{uptime:.1f}%")
    
    # Recent errors
    st.subheader("⚠️ Recent Errors")
    
    errors_found = False
    for env in ['dev', 'stage', 'prod']:
        log_file = f'logs/{env}/{app_name}_deployment_log.csv'
        
        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            errors = df[df['status'] == 'failure']
            
            if not errors.empty:
                errors_found = True
                st.write(f"**{env.upper()}:** {len(errors)} errors")
                st.dataframe(errors.tail(3), use_container_width=True)
    
    if not errors_found:
        st.success("No recent errors! 🎉")

def main():
    st.set_page_config(page_title="App Dashboard", layout="wide", page_icon="📱")
    
    st.title("📱 Application Dashboard")
    st.markdown("*App-centric view of onboarded applications*")
    
    # Sidebar for app selection
    st.sidebar.title("🔍 App Selection")
    
    apps = load_onboarded_apps()
    
    if apps:
        app_names = ['Overview'] + [app['name'] for app in apps]
        selected = st.sidebar.selectbox("Select View", app_names)
        
        st.divider()
        
        if selected == 'Overview':
            render_apps_overview()
        else:
            render_app_details(selected)
    else:
        render_apps_overview()
    
    # Footer
    st.markdown("---")
    st.markdown("*Dashboard for Uday's UI integration*")

if __name__ == "__main__":
    main()