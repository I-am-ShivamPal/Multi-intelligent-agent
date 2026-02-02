import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Student Performance Analytics", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('dataset/student.csv')

df = load_data()

st.title("📊 Student Performance Analytics Dashboard")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Students", len(df))
col2.metric("Avg Score", f"{df['total_score'].mean():.1f}")
col3.metric("A Grade %", f"{(df['grade']=='A').sum()/len(df)*100:.1f}%")
col4.metric("Avg Study Hours", f"{df['weekly_self_study_hours'].mean():.1f}h")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 3D Analysis", "🔥 Heatmap", "📈 Parallel Coords", "🎪 Sunburst"])

with tab1:
    fig = px.scatter_3d(df, x='weekly_self_study_hours', y='attendance_percentage', 
                        z='total_score', color='grade', size='class_participation',
                        title="3D Performance Space", height=600,
                        color_discrete_map={'A':'#00cc96','B':'#636efa','C':'#ffa15a','D':'#ef553b','F':'#ab63fa'})
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    corr = df[['weekly_self_study_hours','attendance_percentage','class_participation','total_score']].corr()
    fig = px.imshow(corr, text_auto=True, aspect="auto", 
                    title="Feature Correlation Heatmap",
                    color_continuous_scale='RdBu_r')
    st.plotly_chart(fig, use_container_width=True)
    
    pivot = df.groupby(['grade'])['total_score'].describe()[['mean','std','min','max']].T
    fig2 = px.imshow(pivot, text_auto='.1f', aspect="auto",
                     title="Grade Statistics Heatmap", labels=dict(color="Value"))
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig = px.parallel_coordinates(df, 
                                  dimensions=['weekly_self_study_hours','attendance_percentage',
                                            'class_participation','total_score'],
                                  color='total_score', 
                                  color_continuous_scale='Viridis',
                                  title="Parallel Coordinates - Student Profiles")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    df_sun = df.copy()
    df_sun['score_range'] = pd.cut(df_sun['total_score'], bins=[0,60,80,90,100], labels=['<60','60-80','80-90','90+'])
    df_sun['study_range'] = pd.cut(df_sun['weekly_self_study_hours'], bins=[0,10,20,50], labels=['Low','Med','High'])
    
    fig = px.sunburst(df_sun, path=['grade','score_range','study_range'], 
                      title="Grade Distribution Hierarchy",
                      color='grade', height=600)
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("🎻 Distribution Analysis")
col1, col2 = st.columns(2)

with col1:
    fig = go.Figure()
    for grade in sorted(df['grade'].unique()):
        fig.add_trace(go.Violin(y=df[df['grade']==grade]['total_score'], 
                                name=grade, box_visible=True, meanline_visible=True))
    fig.update_layout(title="Score Distribution by Grade (Violin Plot)", showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.box(df, x='grade', y='weekly_self_study_hours', color='grade',
                 title="Study Hours by Grade (Box Plot)", points="all")
    st.plotly_chart(fig, use_container_width=True)
