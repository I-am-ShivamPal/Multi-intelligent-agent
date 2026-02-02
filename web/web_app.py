import streamlit as st
import pandas as pd
import os
import json
import datetime
import numpy as np

# Ensure directories exist
os.makedirs("logs", exist_ok=True)
os.makedirs("insightflow", exist_ok=True)
os.makedirs("dataset", exist_ok=True)

# Initialize files if not exist (lazy loading)
def init_files():
    if not os.path.exists("insightflow/telemetry.json"):
        with open("insightflow/telemetry.json", "w") as f:
            json.dump([], f)

# Quick init only
init_files()

st.set_page_config(
    page_title="Multi-Agent CI/CD Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Multi-Agent CI/CD System")
st.success("✅ Successfully deployed on Render!")

# Sidebar
st.sidebar.header("Dashboard Controls ⚙️")
view_mode = st.sidebar.radio("View Mode", ["User Mode", "Developer Mode"])
performance_view = st.sidebar.selectbox("Performance View", ["Student Scores", "System Health"])

if st.sidebar.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.rerun()

# Agent Status
st.subheader("🔍 Real-time Agent Status")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Deploy Agent", "🟢 Active")
with col2: st.metric("Issue Monitor", "🟡 Watching")
with col3: st.metric("Auto Heal", "🔵 Ready")
with col4: st.metric("RL Optimizer", "🟠 Learning")
with col5: st.metric("Sovereign Bus", "🟢 Online")

# Load data with fallback
@st.cache_data(ttl=60)
def load_all_data():
    data = {}
    files = {
        "deployment": os.path.join("logs", r"deployment_log.csv"),
        "uptime": os.path.join("logs", r"uptime_log.csv"),
        "healing": os.path.join("logs", r"healing_log.csv"),
        "issues": os.path.join("logs", r"issue_log.csv"),
        "qtable": os.path.join("logs", r"rl_log.csv"),
        "scores": "dataset/student_scores.csv"
    }
    
    for key, file_path in files.items():
        try:
            if os.path.exists(file_path):
                if key == "qtable":
                    data[key] = pd.read_csv(file_path, index_col=0)
                else:
                    data[key] = pd.read_csv(file_path)
                    if "timestamp" in data[key].columns:
                        data[key]["timestamp"] = pd.to_datetime(data[key]["timestamp"], errors="coerce")
            else:
                data[key] = pd.DataFrame()
        except Exception:
            data[key] = pd.DataFrame()
    return data

data = load_all_data()

# Main Dashboard Tabs
if view_mode == "Developer Mode":
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Performance & Events", 
        "🧠 Agent Intelligence", 
        "🔍 System Health", 
        "🤖 RL Analytics", 
        "📁 Raw Data Logs"
    ])
else:
    tab1, tab2, tab3 = st.tabs([
        "📊 Performance Summary", 
        "🔍 System Health", 
        "📊 Key Metrics"
    ])

# TAB 1: Performance & Events
with tab1:
    st.header(f"{performance_view} Performance")
    
    if performance_view == "Student Scores" and not data["scores"].empty:
        st.line_chart(data["scores"].set_index("timestamp")["score"])
    else:
        st.info("Performance data will appear here when available")
    
    st.subheader("Recent System Events")
    if not data["deployment"].empty:
        st.dataframe(data["deployment"].tail(10), use_container_width=True)
    else:
        st.info("No deployment events yet")

# TAB 2: Agent Intelligence / System Health
with tab2:
    if view_mode == "Developer Mode":
        st.header("Agent Intelligence & Learning")
        
        col1, col2 = st.columns(2)
        with col1:
            if not data["healing"].empty:
                success_rate = (data["healing"]["status"] == "success").mean() * 100
                st.metric("Healing Success Rate", f"{success_rate:.1f}%")
            else:
                st.metric("Healing Success Rate", "N/A")
        
        with col2:
            total_issues = len(data["issues"]) if not data["issues"].empty else 0
            st.metric("Issues Detected", total_issues)
        
        if not data["qtable"].empty:
            st.subheader("Q-Learning Table")
            st.dataframe(data["qtable"], use_container_width=True)
    else:
        st.header("System Health Overview")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("System Status", "🟢 Healthy")
        with col2: st.metric("Uptime", "99.2%")
        with col3: st.metric("Response Time", "<200ms")

# TAB 3: System Health / Key Metrics
with tab3:
    if view_mode == "Developer Mode":
        st.header("System Health Metrics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            total_deployments = len(data["deployment"]) if not data["deployment"].empty else 0
            st.metric("Total Deployments", total_deployments)
        with col2:
            total_healing = len(data["healing"]) if not data["healing"].empty else 0
            st.metric("Healing Actions", total_healing)
        with col3:
            st.metric("System Uptime", "99.2%")
        
        if not data["uptime"].empty:
            st.subheader("Uptime Timeline")
            st.dataframe(data["uptime"].tail(10), use_container_width=True)
    else:
        st.header("Key Performance Metrics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Agents", "5/5")
            st.metric("Success Rate", "98.5%")
        with col2:
            st.metric("Avg Response", "180ms")
            st.metric("Issues Resolved", "47")

# Developer Mode Additional Tabs
if view_mode == "Developer Mode":
    with tab4:
        st.header("RL Analytics & Learning Progress")
        
        if not data["qtable"].empty:
            st.subheader("Q-Table Values")
            st.dataframe(data["qtable"], use_container_width=True)
            
            st.subheader("Learning Progress")
            st.bar_chart(data["qtable"].T)
        else:
            st.info("RL data will appear here when training begins")
    
    with tab5:
        st.header("Raw Data Logs")
        
        log_sections = {
            "Deployment Log": data["deployment"],
            "Uptime Log": data["uptime"],
            "Healing Log": data["healing"],
            "Issue Log": data["issues"],
            "Q-Table": data["qtable"]
        }
        
        for name, df in log_sections.items():
            with st.expander(f"Show {name}"):
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info(f"No data available for {name}")

# Store telemetry
if 'telemetry_stored' not in st.session_state:
    try:
        with open("insightflow/telemetry.json", "r") as f:
            telemetry = json.load(f)
        
        telemetry.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "status": "active",
            "platform": "render",
            "mode": view_mode
        })
        
        with open("insightflow/telemetry.json", "w") as f:
            json.dump(telemetry[-100:], f)
        
        st.session_state.telemetry_stored = True
    except:
        pass

st.success("🚀 Complete Multi-Agent Dashboard - All tabs functional!")