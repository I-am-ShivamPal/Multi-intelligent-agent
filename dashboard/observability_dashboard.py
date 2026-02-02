#!/usr/bin/env python3
"""
Observability Dashboard
Enhanced dashboard with comprehensive metrics and monitoring
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.metrics_aggregator import MetricsAggregator
from core.env_config import EnvironmentConfig

class ObservabilityDashboard:
    """Enhanced observability dashboard with comprehensive metrics."""
    
    def __init__(self):
        self.aggregator = MetricsAggregator()
        self.environments = ['dev', 'stage', 'prod']
        
        # Configure Streamlit page
        st.set_page_config(
            page_title="CI/CD Observability Dashboard",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    def render_sidebar(self):
        """Render sidebar with controls."""
        st.sidebar.title("🔍 Observability Controls")
        
        # Environment filter
        selected_envs = st.sidebar.multiselect(
            "Select Environments",
            self.environments,
            default=self.environments
        )
        
        # Time range selector
        time_range = st.sidebar.selectbox(
            "Time Range",
            ["Last 1 hour", "Last 6 hours", "Last 24 hours", "Last 7 days"],
            index=2
        )
        
        # Auto-refresh
        auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
        if auto_refresh:
            st.rerun()
        
        # Refresh button
        if st.sidebar.button("🔄 Refresh Now"):
            st.rerun()
        
        return selected_envs, time_range
    
    def render_environment_health(self, selected_envs):
        """Render environment health overview."""
        st.header("🌍 Environment Health Overview")
        
        health_data = self.aggregator.get_environment_health()
        
        # Create columns for each environment
        cols = st.columns(len(selected_envs))
        
        for i, env in enumerate(selected_envs):
            with cols[i]:
                env_health = health_data.get(env, {})
                status = env_health.get('status', 'unknown')
                uptime = env_health.get('uptime_percent', 0)
                
                # Status color mapping
                status_colors = {
                    'healthy': '🟢',
                    'warning': '🟡', 
                    'critical': '🔴',
                    'unknown': '⚪'
                }
                
                st.metric(
                    label=f"{status_colors.get(status, '⚪')} {env.upper()}",
                    value=f"{uptime:.1f}% uptime",
                    delta=f"{env_health.get('services_count', 0)} services"
                )
                
                # Additional metrics
                st.write(f"**Avg Latency:** {env_health.get('avg_latency_ms', 0):.0f}ms")
                st.write(f"**Error Rate:** {env_health.get('error_rate', 0):.1f}%")
                st.write(f"**Last Deploy:** {env_health.get('last_deployment', 'Never')[:16]}")
    
    def render_scaling_activity(self, selected_envs):
        """Render scaling activity visualization."""
        st.header("⚡ Scaling Activity")
        
        scaling_data = self.aggregator.get_scaling_activity()
        
        if scaling_data['environments']:
            # Filter data for selected environments
            filtered_data = {
                'environments': [],
                'worker_counts': [],
                'queue_depths': [],
                'throughput': []
            }
            
            for i, env in enumerate(scaling_data['environments']):
                if env in selected_envs:
                    filtered_data['environments'].append(env)
                    filtered_data['worker_counts'].append(scaling_data['worker_counts'][i])
                    filtered_data['queue_depths'].append(scaling_data['queue_depths'][i])
                    filtered_data['throughput'].append(scaling_data['throughput'][i])
            
            if filtered_data['environments']:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Worker count chart
                    fig_workers = px.bar(
                        x=filtered_data['environments'],
                        y=filtered_data['worker_counts'],
                        title="Active Workers by Environment",
                        labels={'x': 'Environment', 'y': 'Worker Count'},
                        color=filtered_data['worker_counts'],
                        color_continuous_scale='viridis'
                    )
                    st.plotly_chart(fig_workers, use_container_width=True)
                
                with col2:
                    # Queue depth chart
                    fig_queue = px.bar(
                        x=filtered_data['environments'],
                        y=filtered_data['queue_depths'],
                        title="Current Queue Depth",
                        labels={'x': 'Environment', 'y': 'Queue Depth'},
                        color=filtered_data['queue_depths'],
                        color_continuous_scale='reds'
                    )
                    st.plotly_chart(fig_queue, use_container_width=True)
        else:
            st.info("No scaling data available yet. Deploy some workloads to see scaling metrics.")
    
    def render_deployment_throughput(self, selected_envs, time_range):
        """Render deployment throughput over time."""
        st.header("🚀 Deployment Throughput")
        
        # Parse time range
        hours_map = {
            "Last 1 hour": 1,
            "Last 6 hours": 6, 
            "Last 24 hours": 24,
            "Last 7 days": 168
        }
        hours = hours_map.get(time_range, 24)
        
        throughput_data = self.aggregator.get_deployment_throughput(hours)
        
        if throughput_data['timestamps']:
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Deployments per Hour', 'Success Rate %'),
                vertical_spacing=0.1
            )
            
            # Plot deployment counts
            for env in selected_envs:
                if env in throughput_data['environments']:
                    env_data = throughput_data['environments'][env]
                    if env_data['deployments']:
                        fig.add_trace(
                            go.Scatter(
                                x=throughput_data['timestamps'],
                                y=env_data['deployments'],
                                mode='lines+markers',
                                name=f"{env.upper()} Deployments",
                                line=dict(width=2)
                            ),
                            row=1, col=1
                        )
            
            # Plot success rates
            for env in selected_envs:
                if env in throughput_data['environments']:
                    env_data = throughput_data['environments'][env]
                    if env_data['success_rate']:
                        fig.add_trace(
                            go.Scatter(
                                x=throughput_data['timestamps'],
                                y=env_data['success_rate'],
                                mode='lines+markers',
                                name=f"{env.upper()} Success Rate",
                                line=dict(width=2, dash='dot')
                            ),
                            row=2, col=1
                        )
            
            fig.update_layout(height=600, showlegend=True)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_yaxes(title_text="Count", row=1, col=1)
            fig.update_yaxes(title_text="Success Rate (%)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No deployment data available for the selected time range.")
    
    def render_queue_depth_over_time(self, selected_envs):
        """Render queue depth over time."""
        st.header("📊 Queue Depth Over Time")
        
        queue_data = self.aggregator.get_queue_depth_over_time()
        
        if queue_data['timestamps']:
            fig = go.Figure()
            
            for env in selected_envs:
                if env in queue_data['environments'] and queue_data['environments'][env]:
                    fig.add_trace(
                        go.Scatter(
                            x=queue_data['timestamps'],
                            y=queue_data['environments'][env],
                            mode='lines+markers',
                            name=f"{env.upper()} Queue",
                            fill='tonexty' if env != selected_envs[0] else 'tozeroy',
                            line=dict(width=2)
                        )
                    )
            
            fig.update_layout(
                title="Queue Depth Trends (Last 6 Hours)",
                xaxis_title="Time",
                yaxis_title="Queue Depth",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No queue depth data available yet.")
    
    def render_risk_category_timeline(self, selected_envs):
        """Render risk category over time."""
        st.header("⚠️ Risk Category vs Timestamp")
        
        risk_data = {'timestamps': [], 'environments': {env: [] for env in selected_envs}}
        
        for env in selected_envs:
            issue_log = fos.path.join("logs", r"{env}/issue_log.csv")
            if os.path.exists(issue_log):
                try:
                    df = pd.read_csv(issue_log)
                    if not df.empty and 'timestamp' in df.columns and 'failure_state' in df.columns:
                        df['timestamp'] = pd.to_datetime(df['timestamp'])
                        df['risk_level'] = df['failure_state'].map({
                            'deployment_failure': 3,
                            'latency_issue': 2,
                            'anomaly_health': 3,
                            'anomaly_score': 2,
                            'no_failure': 0
                        }).fillna(1)
                        
                        for _, row in df.iterrows():
                            if row['timestamp'] not in risk_data['timestamps']:
                                risk_data['timestamps'].append(row['timestamp'])
                            risk_data['environments'][env].append({
                                'timestamp': row['timestamp'],
                                'risk': row['risk_level'],
                                'category': row['failure_state']
                            })
                except Exception:
                    pass
        
        if any(risk_data['environments'].values()):
            fig = go.Figure()
            
            colors = {'deployment_failure': 'red', 'latency_issue': 'orange', 
                     'anomaly_health': 'darkred', 'anomaly_score': 'yellow', 'no_failure': 'green'}
            
            for env in selected_envs:
                if risk_data['environments'][env]:
                    timestamps = [d['timestamp'] for d in risk_data['environments'][env]]
                    risks = [d['risk'] for d in risk_data['environments'][env]]
                    categories = [d['category'] for d in risk_data['environments'][env]]
                    
                    fig.add_trace(go.Scatter(
                        x=timestamps, y=risks, mode='lines+markers',
                        name=f"{env.upper()}", line=dict(width=2),
                        marker=dict(size=10, color=[colors.get(c, 'gray') for c in categories]),
                        text=categories, hovertemplate='%{text}<br>Risk: %{y}<br>%{x}'
                    ))
            
            fig.update_layout(
                xaxis_title="Timestamp", yaxis_title="Risk Level (0=None, 3=Critical)",
                height=400, yaxis=dict(range=[-0.5, 3.5])
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No risk data available yet.")
    
    def render_error_heatmap(self, selected_envs):
        """Render error heatmap by environment."""
        st.header("🔥 Error Heatmap by Environment")
        
        error_data = self.aggregator.get_error_heatmap()
        
        if error_data['environments']:
            # Filter for selected environments
            filtered_envs = []
            filtered_errors = []
            filtered_counts = []
            filtered_severity = []
            
            for i, env in enumerate(error_data['environments']):
                if env in selected_envs:
                    filtered_envs.append(env)
                    filtered_errors.append(error_data['error_types'][i])
                    filtered_counts.append(error_data['error_counts'][i])
                    filtered_severity.append(error_data['severity_colors'][i])
            
            if filtered_envs:
                # Create DataFrame for heatmap
                df = pd.DataFrame({
                    'Environment': filtered_envs,
                    'Error Type': filtered_errors,
                    'Count': filtered_counts,
                    'Severity': filtered_severity
                })
                
                # Pivot for heatmap
                heatmap_df = df.pivot_table(
                    index='Error Type', 
                    columns='Environment', 
                    values='Count', 
                    fill_value=0
                )
                
                if not heatmap_df.empty:
                    fig = px.imshow(
                        heatmap_df.values,
                        x=heatmap_df.columns,
                        y=heatmap_df.index,
                        color_continuous_scale='Reds',
                        title="Error Count Heatmap (Last 7 Days)"
                    )
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Error summary table
                    st.subheader("Error Summary")
                    summary_df = df.groupby(['Environment', 'Severity']).agg({
                        'Count': 'sum'
                    }).reset_index()
                    st.dataframe(summary_df, use_container_width=True)
                else:
                    st.success("No errors detected in the selected environments! 🎉")
            else:
                st.info("No error data for selected environments.")
        else:
            st.success("No errors detected across all environments! 🎉")
    
    def render_system_metrics_summary(self):
        """Render system metrics summary."""
        st.header("📈 System Metrics Summary")
        
        # Get overview data
        overview = self.aggregator.get_system_overview()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_deployments = sum(
                len(env_data.get('deployments', [])) 
                for env_data in overview['deployment_throughput']['environments'].values()
            )
            st.metric("Total Deployments", total_deployments)
        
        with col2:
            avg_success_rate = np.mean([
                np.mean(env_data.get('success_rate', [100])) 
                for env_data in overview['deployment_throughput']['environments'].values()
                if env_data.get('success_rate')
            ]) if overview['deployment_throughput']['environments'] else 100
            st.metric("Avg Success Rate", f"{avg_success_rate:.1f}%")
        
        with col3:
            total_workers = sum(overview['scaling_activity']['worker_counts'])
            st.metric("Total Workers", total_workers)
        
        with col4:
            total_queue_depth = sum(overview['scaling_activity']['queue_depths'])
            st.metric("Total Queue Depth", total_queue_depth)
    
    def run(self):
        """Run the observability dashboard."""
        st.title("📊 CI/CD Observability Dashboard")
        st.markdown("*Real-time monitoring and metrics for multi-environment CI/CD system*")
        
        # Render sidebar
        selected_envs, time_range = self.render_sidebar()
        
        # Main dashboard content
        self.render_system_metrics_summary()
        
        st.divider()
        
        self.render_environment_health(selected_envs)
        
        st.divider()
        
        self.render_scaling_activity(selected_envs)
        
        st.divider()
        
        self.render_deployment_throughput(selected_envs, time_range)
        
        st.divider()
        
        self.render_queue_depth_over_time(selected_envs)
        
        st.divider()
        
        self.render_risk_category_timeline(selected_envs)
        
        st.divider()
        
        self.render_error_heatmap(selected_envs)
        
        # Footer
        st.markdown("---")
        st.markdown("*Dashboard auto-refreshes every 30 seconds when enabled*")

if __name__ == "__main__":
    dashboard = ObservabilityDashboard()
    dashboard.run()