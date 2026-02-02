#!/usr/bin/env python3
"""App Control Panel - Deploy, Scale, Test Applications"""
import streamlit as st
import os
import sys
import json
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator.app_orchestrator import AppOrchestrator

def load_onboarded_apps():
    """Load apps from registry."""
    registry_path = 'apps/registry'
    apps = []
    
    if os.path.exists(registry_path):
        for file in os.listdir(registry_path):
            if file.endswith('.json'):
                with open(os.path.join(registry_path, file)) as f:
                    apps.append(json.load(f))
    
    return apps

def render_app_selector():
    """Render app and environment selector."""
    apps = load_onboarded_apps()
    
    if not apps:
        st.warning("No apps onboarded. Please onboard apps first.")
        return None, None
    
    col1, col2 = st.columns(2)
    
    with col1:
        app_names = [app['name'] for app in apps]
        selected_app = st.selectbox("Select Application", app_names)
    
    with col2:
        selected_env = st.selectbox("Select Environment", ['dev', 'stage', 'prod'])
    
    return selected_app, selected_env

def render_deploy_section(app_name, env):
    """Render deploy controls."""
    st.subheader("🚀 Deploy Application")
    
    if st.button(f"Deploy {app_name} to {env.upper()}", type="primary"):
        with st.spinner(f"Deploying {app_name} to {env}..."):
            try:
                orchestrator = AppOrchestrator(env)
                result = orchestrator.deploy_app(app_name, env)
                
                if result['success']:
                    st.success(f"✅ {app_name} deployed successfully!")
                    st.json(result)
                else:
                    st.error(f"❌ Deployment failed: {result.get('error')}")
            except Exception as e:
                st.error(f"❌ Error: {e}")

def render_scale_section(app_name, env):
    """Render scale controls."""
    st.subheader("📈 Scale Workers")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        workers = st.slider("Number of Workers", 1, 10, 3)
    
    with col2:
        if st.button("Scale", type="secondary"):
            with st.spinner(f"Scaling {app_name} to {workers} workers..."):
                try:
                    orchestrator = AppOrchestrator(env)
                    result = orchestrator.scale_app(app_name, workers, env)
                    
                    if result['success']:
                        st.success(f"✅ Scaled to {workers} workers!")
                        st.json(result)
                    else:
                        st.error(f"❌ Scaling failed: {result.get('error')}")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

def render_test_scenario_section(app_name, env):
    """Render test scenario controls."""
    st.subheader("🧪 Trigger Test Scenario")
    
    scenario = st.selectbox(
        "Select Test Scenario",
        ["Deploy → Failure → Scale → Stop", "Multi-App Test", "Load Test"]
    )
    
    if st.button("Run Test Scenario"):
        with st.spinner(f"Running test scenario: {scenario}..."):
            try:
                if scenario == "Deploy → Failure → Scale → Stop":
                    result = subprocess.run(
                        [sys.executable, "orchestrator/test_orchestrator.py", "--scenario", "workflow"],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Test scenario completed successfully!")
                        with st.expander("Test Output"):
                            st.code(result.stdout)
                    else:
                        st.error("❌ Test scenario failed")
                        with st.expander("Error Output"):
                            st.code(result.stderr)
                
                elif scenario == "Multi-App Test":
                    result = subprocess.run(
                        [sys.executable, "orchestrator/test_orchestrator.py", "--scenario", "multi-app"],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Multi-app test completed!")
                        with st.expander("Test Output"):
                            st.code(result.stdout)
                    else:
                        st.error("❌ Test failed")
                
                else:
                    st.info("Load test scenario coming soon...")
                    
            except Exception as e:
                st.error(f"❌ Error running test: {e}")

def render_app_status(app_name, env):
    """Render current app status."""
    st.subheader("📊 Current Status")
    
    try:
        orchestrator = AppOrchestrator(env)
        status = orchestrator.get_app_status(app_name)
        
        if status:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", status['status'].upper())
            with col2:
                st.metric("Workers", status.get('workers', 0))
            with col3:
                st.metric("Environment", status['environment'].upper())
            
            with st.expander("Full Status Details"):
                st.json(status)
        else:
            st.info(f"{app_name} not deployed in {env}")
    
    except Exception as e:
        st.warning(f"Could not load status: {e}")

def render_app_logs(app_name, env):
    """Render app-specific logs."""
    st.subheader("📋 Application Logs")
    
    tab1, tab2 = st.tabs(["Deployment Log", "Health Log"])
    
    with tab1:
        log_file = f'logs/{env}/{app_name}_deployment_log.csv'
        if os.path.exists(log_file):
            import pandas as pd
            df = pd.read_csv(log_file)
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("No deployment logs yet")
    
    with tab2:
        health_file = f'logs/{env}/{app_name}_health_log.csv'
        if os.path.exists(health_file):
            import pandas as pd
            df = pd.read_csv(health_file)
            st.dataframe(df.tail(10), use_container_width=True)
        else:
            st.info("No health logs yet")

def main():
    st.set_page_config(page_title="App Control Panel", layout="wide", page_icon="🎛️")
    
    st.title("🎛️ Application Control Panel")
    st.markdown("*Deploy, scale, and test applications across environments*")
    
    # App selector
    app_name, env = render_app_selector()
    
    if not app_name or not env:
        return
    
    st.divider()
    
    # Current status
    render_app_status(app_name, env)
    
    st.divider()
    
    # Control sections
    col1, col2 = st.columns(2)
    
    with col1:
        render_deploy_section(app_name, env)
        st.divider()
        render_scale_section(app_name, env)
    
    with col2:
        render_test_scenario_section(app_name, env)
    
    st.divider()
    
    # Logs
    render_app_logs(app_name, env)
    
    # Footer
    st.markdown("---")
    st.markdown("*Control panel for Vinayak's testing and Uday's UI integration*")

if __name__ == "__main__":
    main()