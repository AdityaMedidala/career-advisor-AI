import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core.scoring import load_occupations

st.title("📊 Job Market Insights")
st.info("Compare the required skill sets for different roles in our dataset.")

occupations = load_occupations()

if not occupations:
    st.error("Occupation data could not be loaded.")
    st.stop()

role_names = [o['occupation'] for o in occupations]
selected_roles = st.multiselect(
    "Select up to 3 roles to compare:",
    options=role_names,
    max_selections=3,
    default=[role_names[0], role_names[1]] if len(role_names) >= 2 else None
)

if len(selected_roles) < 2:
    st.warning("Please select at least two roles to compare.")
    st.stop()

top_skills = set()
for role_name in selected_roles:
    role_data = next((o for o in occupations if o['occupation'] == role_name), None)
    if role_data:
        sorted_skills = sorted(role_data['skills_required'], key=lambda x: x['weight'], reverse=True)
        for skill_obj in sorted_skills[:7]:
            top_skills.add(skill_obj['skill'])
skill_axes = sorted(list(top_skills))

chart_data = []
for role_name in selected_roles:
    role_data = next((o for o in occupations if o['occupation'] == role_name), None)
    if role_data:
        skill_map = {s['skill']: s['weight'] for s in role_data['skills_required']}
        weights = [skill_map.get(skill, 0) for skill in skill_axes]
        chart_data.append(go.Scatterpolar(r=weights, theta=skill_axes, fill='toself', name=role_name))

if chart_data:
    fig = go.Figure(data=chart_data)
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=True,
        title="Skill Importance Comparison (1=Low, 5=High)",
        margin=dict(l=40, r=40, t=80, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)