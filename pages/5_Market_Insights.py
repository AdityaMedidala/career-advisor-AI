import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from core.scoring import load_occupations
from datetime import datetime, timedelta
import random

st.title("📊 Market Insights")
st.markdown("### Key career opportunities and market trends")

# Load data
occupations = load_occupations()
user_skills = st.session_state.get("skills", [])

if not occupations:
    st.error("Unable to load occupation data.")
    st.stop()

# Simple sidebar
with st.sidebar:
    st.markdown("### 🎯 Quick Filters")
    
    # Role categories
    all_roles = [o['occupation'] for o in occupations]
    selected_roles = st.multiselect(
        "Focus on roles:",
        options=all_roles,
        default=all_roles[:3] if len(all_roles) >= 3 else all_roles,
        help="Choose specific roles to analyze"
    )

# Main dashboard tabs
tab1, tab2, tab3 = st.tabs(["📈 Market Overview", "🎯 Role Analysis", "💰 Salary Insights"])

with tab1:
    st.markdown("## 📈 Market Overview")
    
    # Key metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Career Paths", len(occupations))
    with col2:
        all_skills = set()
        for occ in occupations:
            for skill_obj in occ.get('skills_required', []):
                all_skills.add(skill_obj['skill'])
        st.metric("Unique Skills Tracked", len(all_skills))
    with col3:
        if user_skills:
            user_role_matches = sum(1 for occ in occupations 
                                  if any(skill['skill'] in user_skills 
                                        for skill in occ.get('skills_required', [])))
            st.metric("Your Compatible Roles", f"{user_role_matches}/{len(occupations)}")
        else:
            st.metric("Market Coverage", "Complete")
    
    # Top skills chart
    st.markdown("### 🔥 Most In-Demand Skills")
    
    skill_counts = {}
    for occ in occupations:
        for skill_obj in occ.get('skills_required', []):
            skill = skill_obj['skill']
            if skill in skill_counts:
                skill_counts[skill] += 1
            else:
                skill_counts[skill] = 1
    
    # Create distribution chart
    popularity_df = pd.DataFrame([
        {'Skill': skill, 'Frequency': count}
        for skill, count in skill_counts.items()
    ]).sort_values('Frequency', ascending=False).head(10)
    
    fig_popularity = px.bar(
        popularity_df,
        x='Frequency',
        y='Skill',
        orientation='h',
        title="Top 10 Most Required Skills"
    )
    fig_popularity.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_popularity, use_container_width=True)

with tab2:
    st.markdown("## 🎯 Role Analysis")
    
    if not selected_roles:
        st.warning("Please select at least one role from the sidebar to analyze.")
    else:
        # Simple role comparison
        for role_name in selected_roles:
            role = next(occ for occ in occupations if occ['occupation'] == role_name)
            
            with st.expander(f"📋 {role_name}", expanded=len(selected_roles) == 1):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Skills breakdown
                    skills_df = pd.DataFrame(role['skills_required']).sort_values('weight', ascending=False)
                    
                    fig_skills = px.bar(
                        skills_df.head(10),  # Show only top 10 skills
                        x='weight',
                        y='skill',
                        orientation='h',
                        color='weight',
                        title=f"Top Skills for {role_name}",
                        color_continuous_scale='Viridis'
                    )
                    fig_skills.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_skills, use_container_width=True)
                
                with col2:
                    # Role statistics
                    total_skills = len(role['skills_required'])
                    critical_skills = len([s for s in role['skills_required'] if s['weight'] >= 4])
                    
                    st.metric("Total Skills Required", total_skills)
                    st.metric("Critical Skills (4-5)", critical_skills)
                    
                    # User compatibility
                    if user_skills:
                        user_matches = [s for s in role['skills_required'] if s['skill'] in user_skills]
                        match_score = len(user_matches) / total_skills * 100
                        
                        st.metric("Your Match Score", f"{match_score:.0f}%")
                        
                        if user_matches:
                            st.success("✅ Your matching skills:")
                            for skill in user_matches[:3]:
                                st.write(f"• {skill['skill']}")

with tab3:
    st.markdown("## 💰 Salary Insights")
    
    # Simulated salary data based on skill complexity
    st.info("💡 Salary estimates are based on skill complexity and market demand")
    
    salary_data = []
    for occ in occupations:
        # Calculate salary based on skills complexity and market demand
        skill_complexity = sum(s['weight'] for s in occ['skills_required'])
        num_skills = len(occ['skills_required'])
        
        # Base salary calculation (simulated)
        base_salary = 45000 + (skill_complexity * 6000) + (num_skills * 2500)
        
        # Add some randomization for realism
        variation = random.uniform(0.85, 1.15)
        estimated_salary = int(base_salary * variation)
        
        # Skill premium calculation
        premium_skills = ['AI', 'Machine Learning', 'AWS', 'Kubernetes', 'React', 'Python']
        has_premium = any(premium in [s['skill'] for s in occ['skills_required']] 
                         for premium in premium_skills)
        
        if has_premium:
            estimated_salary = int(estimated_salary * 1.2)
        
        salary_data.append({
            'Role': occ['occupation'],
            'Estimated_Salary': estimated_salary,
            'Has_Premium_Skills': has_premium
        })
    
    salary_df = pd.DataFrame(salary_data).sort_values('Estimated_Salary', ascending=False)
    
    # Salary visualization
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Top Paying Roles")
        
        fig_salary = px.bar(
            salary_df.head(10),  # Show only top 10
            x='Estimated_Salary',
            y='Role',
            color='Has_Premium_Skills',
            title="Top 10 Highest Paying Roles",
            color_discrete_map={True: '#4CAF50', False: '#FFA726'}
        )
        fig_salary.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_salary, use_container_width=True)
    
    with col2:
        st.markdown("### 💎 Key Insights")
        
        highest_salary = salary_df.iloc[0]
        st.metric("Highest Paying Role", highest_salary['Role'])
        st.metric("Top Salary", f"${highest_salary['Estimated_Salary']:,}")
        
        avg_salary = salary_df['Estimated_Salary'].mean()
        st.metric("Market Average", f"${avg_salary:,.0f}")
        
        premium_avg = salary_df[salary_df['Has_Premium_Skills']]['Estimated_Salary'].mean()
        regular_avg = salary_df[~salary_df['Has_Premium_Skills']]['Estimated_Salary'].mean()
        premium_boost = ((premium_avg - regular_avg) / regular_avg) * 100
        
        st.metric("Premium Skills Boost", f"+{premium_boost:.0f}%")

# Bottom action panel
st.divider()
st.markdown("## 🚀 Take Action")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Update My Skills", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

with col2:
    if st.button("🎯 Find Opportunities", use_container_width=True):
        st.switch_page("pages/2_Matches.py")

with col3:
    if st.button("🗺️ Create Learning Plan", use_container_width=True):
        st.switch_page("pages/3_Roadmap.py")