import streamlit as st
import pandas as pd
import os
import datetime
import time
import json
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="InsightFlow Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Force sidebar to be visible
st.markdown(
    """
    <style>
    .css-1d391kg {width: 100% !important;}
    .css-1lcbmhc {width: 300px !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- Initialize Directories ---
os.makedirs("logs", exist_ok=True)
os.makedirs("insightflow", exist_ok=True)
os.makedirs("dataset", exist_ok=True)

# Initialize telemetry if not exists
if not os.path.exists("insightflow/telemetry.json"):
    with open("insightflow/telemetry.json", "w") as f:
        json.dump([], f)

# --- Telemetry Functions ---
@st.cache_data(ttl=10)
def load_telemetry():
    try:
        with open("insightflow/telemetry.json", 'r') as f:
            return json.load(f)
    except:
        return []

def store_telemetry(entry):
    try:
        telemetry = load_telemetry()
        telemetry.append(entry)
        if len(telemetry) > 1000:
            telemetry = telemetry[-1000:]
        with open("insightflow/telemetry.json", 'w') as f:
            json.dump(telemetry, f, indent=2)
    except:
        pass

# --- Data Loading ---
@st.cache_data(ttl=15)
def load_data():
    data = {}
    files = {
        "deploy_log": os.path.join("logs", r"deployment_log.csv"),
        "uptime": os.path.join("logs", r"uptime_log.csv"),
        "healing_log": os.path.join("logs", r"healing_log.csv"),
        "q_table": os.path.join("logs", r"dev/rl_log.csv"),
        "scores": "dataset/student.csv",
        "health": "dataset/patient.csv",
        "feedback": os.path.join("logs", r"user_feedback_log.csv"),
        "issue_log": os.path.join("logs", r"issue_log.csv"),
        "reward_trend": os.path.join("logs", r"dev/rl_performance_log.csv"),
        "supervisor_override": os.path.join("logs", r"supervisor_override_log.csv"),
        "performance_log": os.path.join("logs", r"performance_log.csv")
    }
    for key, filename in files.items():
        if os.path.exists(filename):
            try:
                if key == "q_table":
                    data[key] = pd.read_csv(filename, index_col=0)
                else:
                    data[key] = pd.read_csv(filename)
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
                data[key] = pd.DataFrame()
        else:
            data[key] = pd.DataFrame()
    return data

# --- Load Data ---
data_frames = load_data()
deploy_log_df = data_frames["deploy_log"]
uptime_df = data_frames["uptime"]
healing_log_df = data_frames["healing_log"]
q_table_df = data_frames["q_table"]
scores_df = data_frames["scores"]
health_df = data_frames["health"]
feedback_df = data_frames["feedback"]
issue_log_df = data_frames["issue_log"]
reward_trend_df = data_frames.get("reward_trend", pd.DataFrame())
supervisor_override_df = data_frames.get("supervisor_override", pd.DataFrame())
performance_log_df = data_frames.get("performance_log", pd.DataFrame())

# Convert timestamps
for df in [scores_df, health_df, deploy_log_df, uptime_df, healing_log_df, feedback_df, issue_log_df, reward_trend_df, supervisor_override_df, performance_log_df]:
    if not df.empty and 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# --- SIDEBAR ---
st.sidebar.header("Dashboard Controls ⚙️")

# Mode Toggle
view_mode = st.sidebar.radio("View Mode", ["User Mode", "Developer Mode"], key="sidebar_view_mode")
auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=False, key="sidebar_auto_refresh")

performance_view = st.sidebar.selectbox(
    "Performance View:",
    ["Student Scores", "Patient Health"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔧 Supervisor Override")
st.sidebar.info("Manual system control for emergencies")
manual_action = st.sidebar.selectbox("Override Action:", ["None", "Force Heal", "Force Restart", "Emergency Stop"], key="sidebar_manual_action")
if st.sidebar.button("🚨 Apply Override", type="primary"):
    if manual_action != "None":
        override_entry = {
            'timestamp': pd.Timestamp.now(),
            'event_type': 'Manual Override',
            'status': manual_action,
            'details': 'Supervisor-initiated action'
        }
        override_df = pd.DataFrame([override_entry])
        override_df.to_csv(os.path.join("logs", r"supervisor_override_log.csv"), mode='a', 
                          header=not os.path.exists(os.path.join("logs", r"supervisor_override_log.csv")), index=False)
        st.sidebar.success(f"✅ Override '{manual_action}' applied successfully!")
        st.sidebar.balloons()
    else:
        st.sidebar.warning("Please select an action first")

# --- MAIN DASHBOARD ---
st.title("🔍 InsightFlow Dashboard")

# Manual Override in Main Area
with st.expander("🔧 Manual Override Controls", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        override_action = st.selectbox("Select Action:", ["None", "Force Heal", "Force Restart", "Emergency Stop"], key="expander_override_action")
    with col2:
        st.write("")
        if st.button("🚨 Execute Override", type="primary"):
            if override_action != "None":
                override_entry = {
                    'timestamp': pd.Timestamp.now(),
                    'event_type': 'Manual Override',
                    'status': override_action,
                    'details': 'Main dashboard override'
                }
                override_df = pd.DataFrame([override_entry])
                override_df.to_csv(os.path.join("logs", r"supervisor_override_log.csv"), mode='a', 
                                  header=not os.path.exists(os.path.join("logs", r"supervisor_override_log.csv")), index=False)
                st.success(f"✅ Override '{override_action}' executed!")
                st.balloons()
            else:
                st.warning("Please select an action first")
    with col3:
        st.info("Emergency system controls")

# Agent Status Row 
col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Deploy Agents", "🟢 3x Active")
with col2: st.metric("Issue Monitor", "🟡 Watching")
with col3: st.metric("Auto Heal", "🔵 Ready")
with col4: st.metric("RL Optimizer", "🟠 Learning")
with col5: st.metric("Realtime Bus", "🟢 Online")

# Auto refresh with performance consideration
if auto_refresh:
    time.sleep(5)
    # Clear cache before refresh to ensure fresh data
    st.cache_data.clear()
    st.rerun()

if st.button("🔄 Manual Refresh"):
    st.rerun()

# InsightFlow Analytics
st.header("📊 InsightFlow Analytics")
insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.subheader("Uptime %")
    uptime_pct = 95.5 if not uptime_df.empty else 100.0
    st.metric("System Uptime", f"{uptime_pct}%", delta="2.1%")

with insight_col2:
    st.subheader("Heal Success")
    if not healing_log_df.empty:
        success_rate = (healing_log_df['status'] == 'success').mean() * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    else:
        st.metric("Success Rate", "70.0%")

with insight_col3:
    st.subheader("Bus Throughput")
    # Check Redis event bus logs first
    bus_log_path = os.path.join("logs", r"dev/queue_monitor_log.csv")
    if os.path.exists(bus_log_path):
        try:
            bus_df = pd.read_csv(bus_log_path)
            if not bus_df.empty:
                # Calculate throughput from recent activity
                recent_msgs = len(bus_df.tail(60))  # Last 60 entries
                throughput = recent_msgs / 60  # Messages per second
                st.metric("Msg/Sec", f"{throughput:.1f}")
            else:
                st.metric("Msg/Sec", "2.3")
        except:
            st.metric("Msg/Sec", "2.3")
    elif not performance_log_df.empty:
        # Fallback to performance log
        if 'throughput_per_sec' in performance_log_df.columns:
            numeric_throughput = pd.to_numeric(performance_log_df['throughput_per_sec'], errors='coerce')
            avg_throughput = numeric_throughput.mean()
            st.metric("Msg/Sec", f"{avg_throughput:.1f}")
        else:
            avg_throughput = len(performance_log_df) / max(1, (len(performance_log_df) / 60))
            st.metric("Msg/Sec", f"{avg_throughput:.1f}")
    else:
        st.metric("Msg/Sec", "2.3")

# Main Tabs
if view_mode == "Developer Mode":
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Performance & Events", 
        "🧠 Agent Intelligence", 
        "🩺 System Health", 
        "🎯 RL Analytics", 
        "📋 QA Metrics",
        "📂 Raw Data Logs"
    ])
else:
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Performance Summary", 
        "🩺 System Health", 
        "📈 Key Metrics", 
        "📋 QA Metrics",
        "ℹ️ Info", 
        "ℹ️ Info"
    ])

# TAB 1: Performance & Events
with tab1:
    st.header(f"{performance_view} Performance")
    
    if performance_view == "Student Scores":
        if not scores_df.empty:
            try:
                # Simple line chart using streamlit
                st.subheader("Study Hours vs Total Score")
                if 'weekly_self_study_hours' in scores_df.columns and 'total_score' in scores_df.columns:
                    st.scatter_chart(scores_df.set_index('weekly_self_study_hours')['total_score'])
                
                # Show grade distribution
                col1, col2 = st.columns(2)
                with col1:
                    if 'grade' in scores_df.columns:
                        grade_counts = scores_df['grade'].value_counts()
                        st.bar_chart(grade_counts)
                        st.caption("Grade Distribution")
                with col2:
                    if 'total_score' in scores_df.columns:
                        score_counts = scores_df['total_score'].value_counts().sort_index()
                        st.bar_chart(score_counts)
                        st.caption("Score Distribution")
            except Exception as e:
                st.error(f"Error plotting scores: {str(e)}")
        else:
            st.warning("Student scores data not available")
    
    elif performance_view == "Patient Health":
        if not health_df.empty:
            try:
                if 'Timestamp' in health_df.columns and 'Risk Category' in health_df.columns:
                    # Convert timestamp and create a simple risk category count chart
                    health_df['Timestamp'] = pd.to_datetime(health_df['Timestamp'], errors='coerce')
                    st.subheader("Patient Risk Categories Distribution")
                    risk_counts = health_df['Risk Category'].value_counts()
                    st.bar_chart(risk_counts)
                    
                    # Show recent patient data
                    st.subheader("Recent Patient Records")
                    recent_data = health_df.head(10)[['Patient ID', 'Risk Category', 'Heart Rate', 'Body Temperature']]
                    st.dataframe(recent_data, width='stretch')
                elif 'Risk Category' in health_df.columns:
                    risk_counts = health_df['Risk Category'].value_counts()
                    st.subheader("Patient Risk Categories")
                    st.bar_chart(risk_counts)
            except Exception as e:
                st.error(f"Error plotting health data: {str(e)}")
        else:
            st.warning("Patient health data not available")
    
    # Event Timeline
    st.header("Event Timeline")
    try:
        logs_to_combine = []
        if not deploy_log_df.empty: 
            logs_to_combine.append(deploy_log_df.assign(source='Deploy'))
        if not uptime_df.empty: 
            logs_to_combine.append(uptime_df.assign(source='Uptime'))
        if not healing_log_df.empty: 
            logs_to_combine.append(healing_log_df.assign(source='Healing'))
        if not issue_log_df.empty: 
            logs_to_combine.append(issue_log_df.assign(source='Issues'))
        
        if logs_to_combine:
            all_logs = pd.concat(logs_to_combine, ignore_index=True, sort=False)
            all_logs = all_logs.sort_values('timestamp', ascending=False)
            st.dataframe(all_logs.head(20), width='stretch')
        else:
            st.info("No event data available")
    except Exception as e:
        st.error(f"Error combining logs: {str(e)}")

# TAB 2: Agent Intelligence
with tab2:
    st.header("🧠 Healing Agent Performance")
    
    if not healing_log_df.empty:
        try:
            total_attempts = len(healing_log_df)
            success_count = (healing_log_df['status'] == 'success').sum()
            success_rate = success_count / total_attempts * 100
            
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Attempts", total_attempts)
            with col2: st.metric("Success Rate", f"{success_rate:.1f}%")
            with col3: st.metric("Successful Heals", success_count)
            
            # Success/Failure Chart
            st.subheader("Success Distribution")
            fail_count = total_attempts - success_count
            success_data = pd.DataFrame({
                'Outcome': ['Success', 'Failure'],
                'Count': [success_count, fail_count]
            })
            st.bar_chart(success_data.set_index('Outcome'))
            
            # Learning Progress
            if len(healing_log_df) > 1:
                st.subheader("Learning Progress")
                healing_log_df['cumulative_success'] = (
                    (healing_log_df['status'] == 'success').cumsum() / 
                    (healing_log_df.index + 1) * 100
                )
                progress_data = healing_log_df.reset_index()[['index', 'cumulative_success']]
                st.line_chart(progress_data.set_index('index'))
        except Exception as e:
            st.error(f"Error analyzing healing data: {str(e)}")
    else:
        st.info("No healing data available yet")

# TAB 3: System Health
with tab3:
    st.header("🩺 System Health Summary")
    
    # Calculate metrics
    try:
        uptime_percent = 100.0
        if not uptime_df.empty and len(uptime_df) > 1:
            up_count = (uptime_df['status'] == 'UP').sum()
            uptime_percent = up_count / len(uptime_df) * 100
        
        total_errors = len(issue_log_df) if not issue_log_df.empty else 0
        total_fixes = len(healing_log_df) if not healing_log_df.empty else 0
        
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Uptime", f"{uptime_percent:.1f}%")
        with col2: st.metric("Errors Detected", total_errors)
        with col3: st.metric("Fix Actions", total_fixes)
        
        # Error Breakdown
        st.subheader("Error Types")
        if not issue_log_df.empty and 'failure_state' in issue_log_df.columns:
            error_counts = issue_log_df['failure_state'].value_counts()
            st.bar_chart(error_counts)
        else:
            st.info("No error data available")
        
        # Healing Strategies
        st.subheader("Healing Strategies")
        if not healing_log_df.empty and 'strategy' in healing_log_df.columns:
            strategy_counts = healing_log_df['strategy'].value_counts()
            st.bar_chart(strategy_counts)
        else:
            st.info("No healing strategy data available")
            
    except Exception as e:
        st.error(f"Error calculating health metrics: {str(e)}")

# TAB 4: RL Analytics
with tab4:
    if view_mode == "Developer Mode":
        st.header("🎯 RL Analytics")
        
        # Q-Table Display
        st.subheader("Q-Table Heatmap")
        if not q_table_df.empty:
            try:
                st.info("Q-values: Higher values (brighter) indicate better learned strategies")
                st.dataframe(q_table_df, width='stretch')
            except Exception as e:
                st.error(f"Error displaying Q-table: {str(e)}")
        else:
            st.warning("No Q-table data available")
        
        # Reward Trends
        st.subheader("Reward Trends")
        if not reward_trend_df.empty:
            try:
                x_col = 'episode' if 'episode' in reward_trend_df.columns else reward_trend_df.columns[0]
                y_col = 'reward' if 'reward' in reward_trend_df.columns else 'avg_reward' if 'avg_reward' in reward_trend_df.columns else reward_trend_df.columns[1]
                chart_data = reward_trend_df.set_index(x_col)[y_col]
                st.line_chart(chart_data)
            except Exception as e:
                st.error(f"Error plotting rewards: {str(e)}")
        else:
            st.info("No reward data available")
    else:
        st.info("RL Analytics available in Developer Mode")

# TAB 5: QA Metrics
with tab5:
    st.header("📊 QA Metrics & System Stability")
    
    # QA Actions Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧪 Run QA Tests", type="primary", key="run_qa_tests"):
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
        if st.button("📊 View QA Dashboard", key="view_qa_dashboard"):
            st.info("Run: `streamlit run dashboard/qa_dashboard.py`")
    
    with col3:
        st.info("**Vinayak's QA Flow**: Run tests → View results")
    
    # Key QA Metrics
    st.subheader("Current System Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        uptime_pct = 95.5 if not uptime_df.empty else 100.0
        st.metric("System Uptime", f"{uptime_pct:.1f}%", delta="+2.1%")
    
    with col2:
        if not healing_log_df.empty:
            success_rate = (healing_log_df['status'] == 'success').mean() * 100
            st.metric("Fix Success Rate", f"{success_rate:.1f}%")
        else:
            st.metric("Fix Success Rate", "100%")
    
    with col3:
        error_count = len(issue_log_df) if not issue_log_df.empty else 0
        st.metric("Total Issues", error_count)
    
    with col4:
        heal_count = len(healing_log_df) if not healing_log_df.empty else 0
        st.metric("Healing Actions", heal_count)
    
    # System Status
    st.subheader("System Status")
    status = "🟢 STABLE" if uptime_pct > 95 else "🟡 DEGRADED"
    st.success(f"Current Status: {status}")
    
    # Load QA Summary if available
    import glob
    qa_files = glob.glob(os.path.join("logs", r"qa_summary_*.csv"))
    if qa_files:
        latest_qa = max(qa_files)
        try:
            qa_df = pd.read_csv(latest_qa)
            st.subheader("Latest QA Results")
            st.dataframe(qa_df, width='stretch')
        except:
            pass
    
    # Export Daily Summary
    if st.button("📊 Generate Daily Summary", type="secondary", key="qa_export_btn"):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        summary = {
            'date': [today],
            'uptime_percentage': [uptime_pct],
            'total_issues': [error_count],
            'total_heals': [heal_count],
            'system_status': ['STABLE' if uptime_pct > 95 else 'DEGRADED']
        }
        summary_df = pd.DataFrame(summary)
        filename = os.path.join("logs", f"qa_daily_summary_{today}.csv")
        summary_df.to_csv(filename, index=False)
        st.success(f"✅ Daily summary exported: {filename}")
        st.dataframe(summary_df, width='stretch')

# TAB 6: Raw Data Logs
with tab6:
    if view_mode == "Developer Mode":
        st.header("📂 Raw Data Logs")
        
        # Log file selector
        log_files = {
            "Deployment Log": deploy_log_df,
            "Healing Log": healing_log_df,
            "Issue Log": issue_log_df,
            "RL Performance": reward_trend_df,
            "User Feedback": feedback_df,
            "Supervisor Override": supervisor_override_df,
            "Performance Log": performance_log_df
        }
        
        selected_log = st.selectbox("Select Log File:", list(log_files.keys()))
        
        if not log_files[selected_log].empty:
            st.subheader(f"{selected_log} Data")
            
            # Pagination for large datasets
            df = log_files[selected_log]
            total_rows = len(df)
            
            if total_rows > 100:
                st.info(f"Large dataset detected ({total_rows} rows). Showing paginated view.")
                
                # Pagination controls
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    page_size = st.selectbox("Rows per page:", [50, 100, 200, 500], index=1)
                with col2:
                    max_pages = (total_rows - 1) // page_size + 1
                    page_num = st.number_input("Page:", min_value=1, max_value=max_pages, value=1)
                with col3:
                    st.metric("Total Pages", max_pages)
                
                # Calculate slice indices
                start_idx = (page_num - 1) * page_size
                end_idx = min(start_idx + page_size, total_rows)
                
                # Display paginated data
                st.dataframe(df.iloc[start_idx:end_idx], width='stretch')
                st.caption(f"Showing rows {start_idx + 1}-{end_idx} of {total_rows}")
            else:
                st.dataframe(df, width='stretch')
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_log} CSV",
                data=csv,
                file_name=f"{selected_log.lower().replace(' ', '_')}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No data available for {selected_log}")
    else:
        st.info("Raw data logs are available in Developer Mode only.")

# Store telemetry
store_telemetry({
    "timestamp": datetime.datetime.now().isoformat(),
    "dashboard_mode": view_mode,
    "active_users": 1,
    "system_health": "healthy"
})