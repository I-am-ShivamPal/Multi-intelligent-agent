import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Patient Health Analytics", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('dataset/patient.csv')

df = load_data()
df_sorted = df.sort_values('Patient ID').head(200)

st.title("🏥 Patient Health Analytics - Line Plot Analysis")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Patients", len(df))
col2.metric("Avg Heart Rate", f"{df['Heart Rate'].mean():.1f} bpm")
col3.metric("High Risk %", f"{(df['Risk Category']=='High Risk').sum()/len(df)*100:.1f}%")
col4.metric("Avg Temp", f"{df['Body Temperature'].mean():.1f}°C")

st.subheader("📈 Vital Signs Trends Over Time")

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_sorted['Patient ID'], y=df_sorted['Heart Rate'], 
                         mode='lines', name='Heart Rate', line=dict(color='red', width=2)))
fig.add_trace(go.Scatter(x=df_sorted['Patient ID'], y=df_sorted['Oxygen Saturation'], 
                         mode='lines', name='O2 Saturation', line=dict(color='blue', width=2)))
fig.add_trace(go.Scatter(x=df_sorted['Patient ID'], y=df_sorted['Respiratory Rate']*4, 
                         mode='lines', name='Respiratory Rate (x4)', line=dict(color='green', width=2)))
fig.update_layout(title="Multi-Vital Signs Comparison", xaxis_title="Patient ID", yaxis_title="Value", height=500)
st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    fig = px.line(df_sorted, x='Patient ID', y='Body Temperature', color='Risk Category',
                 title="Body Temperature by Risk Category",
                 color_discrete_map={'High Risk':'#ef553b','Low Risk':'#00cc96'})
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(df_sorted, x='Patient ID', y='Systolic Blood Pressure', color='Gender',
                 title="Systolic Blood Pressure by Gender")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.line(df_sorted, x='Patient ID', y='Derived_BMI', color='Risk Category',
                 title="BMI Trends by Risk Category",
                 color_discrete_map={'High Risk':'#ef553b','Low Risk':'#00cc96'})
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(df_sorted, x='Patient ID', y='Derived_MAP', color='Gender',
                 title="Mean Arterial Pressure by Gender")
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📊 Age-Based Analysis")

df_age = df.groupby('Age')[['Heart Rate','Body Temperature','Oxygen Saturation']].mean().reset_index()

fig = go.Figure()
fig.add_trace(go.Scatter(x=df_age['Age'], y=df_age['Heart Rate'], mode='lines+markers', name='Heart Rate'))
fig.add_trace(go.Scatter(x=df_age['Age'], y=df_age['Oxygen Saturation'], mode='lines+markers', name='O2 Saturation'))
fig.update_layout(title="Average Vitals by Age", xaxis_title="Age", yaxis_title="Value")
st.plotly_chart(fig, use_container_width=True)
