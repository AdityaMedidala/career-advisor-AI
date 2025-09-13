import streamlit as st
from core.scoring import load_occupations, rank_roles
from core import jobs
from core import llm
from core.job_scraper import job_scraper
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

st.title("🎯 Your Perfect Job Matches")
st.markdown("### Discover roles that align with your unique skill profile")

skills = st.session_state.get("skills", [])
if not skills:
    st.warning("⚠️ Please create your profile first to find job matches.")
    if st.button("📝 Create Profile Now"):
        st.switch_page("pages/1_Profile.py")
    st.stop()

# Simple sidebar filters
with st.sidebar:
    st.markdown("### 🔍 Quick Filters")
    
    # Skills refinement
    edited_skills = st.multiselect(
        "Your Skills:",
        options=sorted(list(set(skills + ["Python", "SQL", "JavaScript", "AWS", "Docker", "Git", 
                                        "Excel", "Tableau", "React", "Node.js", "Linux", "Agile"]))),
        default=skills,
        key="skills_filter"
    )
    
    # Match filters
    min_score = st.slider("Minimum Match Score %", 0, 100, 20, 5)
    show_count = st.selectbox("Show top matches", [3, 5, 8], index=1)

# Update session skills
st.session_state.skills = edited_skills

# Main content area
if not edited_skills:
    st.error("Please select at least one skill to find matches.")
    st.stop()

# Load and rank occupations
occs = load_occupations()
all_matches = rank_roles(edited_skills, occs, top_k=len(occs))
filtered_matches = [m for m in all_matches if (m['score'] * 100) >= min_score][:show_count]

st.session_state.matches = filtered_matches

# Overview metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Your Skills", len(edited_skills))
with col2:
    best_match = max([m['score'] * 100 for m in filtered_matches]) if filtered_matches else 0
    st.metric("Best Match", f"{best_match:.0f}%")
with col3:
    total_careers = len([m for m in all_matches if m['score'] > 0])
    st.metric("Compatible Careers", total_careers)

st.divider()

# Match results
if not filtered_matches:
    st.warning(f"No matches found with {min_score}% minimum score. Try lowering the threshold or adding more skills.")
    st.info("💡 **Suggestion:** Add more skills to your profile or lower the minimum match score in the sidebar.")
else:
    st.markdown(f"### Your Top {len(filtered_matches)} Career Matches")
    
    for i, m in enumerate(filtered_matches):
        score_percentage = int(m['score'] * 100)
        
        with st.container(border=True):
            # Header with role and score
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {i+1}. {m['occupation']}")
            with col2:
                color = "green" if score_percentage >= 70 else "orange" if score_percentage >= 50 else "red"
                st.markdown(f"<h3 style='color: {color}; text-align: right;'>{score_percentage}%</h3>", 
                          unsafe_allow_html=True)
            
            # Progress bar
            st.progress(score_percentage / 100, text=f"{score_percentage}% Skill Alignment")
            
            # Skills breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                # Matching skills
                required_skills = {s['skill']: s['weight'] for s in m["skills_required"]}
                matching_skills = [skill for skill in edited_skills if skill in required_skills]
                
                if matching_skills:
                    st.markdown("**✅ Your Matching Skills:**")
                    for skill in matching_skills[:5]:  # Show only top 5
                        importance = required_skills[skill]
                        stars = "⭐" * importance
                        st.write(f"• **{skill}** {stars}")
                
            with col2:
                # Skill gaps
                if m["gaps"]:
                    st.markdown("**📚 Skills to Develop:**")
                    gap_importance = {gap: next(s['weight'] for s in m["skills_required"] if s['skill'] == gap) 
                                    for gap in m["gaps"]}
                    sorted_gaps = sorted(m["gaps"], key=lambda x: gap_importance[x], reverse=True)
                    
                    for gap in sorted_gaps[:5]:  # Show only top 5
                        importance = gap_importance[gap]
                        urgency = "🔴 Critical" if importance >= 4 else "🟡 Important" if importance >= 3 else "🟢 Nice to have"
                        st.write(f"• **{gap}** - {urgency}")
                else:
                    st.success("🎉 Perfect skill alignment!")
            
            # Action buttons
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Smart job search
                if st.button("🔍 Smart Job Search", key=f"search_{i}", use_container_width=True):
                    with st.spinner("🔍 Searching for jobs..."):
                        user_skills_set = set(edited_skills)
                        required_skills_set = set(s['skill'] for s in m["skills_required"])
                        matching_user_skills = list(user_skills_set.intersection(required_skills_set))
                        
                        # Create search query with role and skills
                        search_query = f"{m['occupation']} {' '.join(matching_user_skills[:3])}"
                        
                        # Get job recommendations
                        jobs = job_scraper.get_professional_job_recommendations(
                            role=search_query,
                            skills=matching_user_skills,
                            max_results=12
                        )
                        
                        # Store jobs in session state for display
                        st.session_state[f"jobs_{i}"] = jobs
                        st.session_state[f"show_jobs_{i}"] = True
            
            with col2:
                if st.button(f"🎯 Build Roadmap", key=f"roadmap_{i}"):
                    st.session_state.selected_role = m
                    st.switch_page("pages/3_Roadmap.py")
            
            with col3:
                if st.button(f"📊 View Details", key=f"details_{i}"):
                    st.session_state[f"show_details_{i}"] = not st.session_state.get(f"show_details_{i}", False)
            
            # Expandable detailed analysis
            if st.session_state.get(f"show_details_{i}", False):
                with st.expander("📊 Detailed Analysis", expanded=True):
                    st.markdown(f"**All Required Skills for {m['occupation']}:**")
                    for skill_obj in m["skills_required"]:
                        skill = skill_obj['skill']
                        weight = skill_obj['weight']
                        has_skill = skill in edited_skills
                        status = "✅" if has_skill else "❌"
                        st.write(f"{status} **{skill}** (Importance: {weight}/5)")
            
            # Job search results
            if st.session_state.get(f"show_jobs_{i}", False):
                jobs = st.session_state.get(f"jobs_{i}", [])
                if jobs:
                    st.markdown("---")
                    st.markdown(f"### 🎯 Job Opportunities for {m['occupation']}")
                    job_scraper.display_jobs(jobs, f"Jobs for {m['occupation']}", widget_key=f"{i}_{m['occupation']}")
                    
                    # Add a button to hide jobs
                    if st.button("❌ Hide Jobs", key=f"hide_jobs_{i}"):
                        st.session_state[f"show_jobs_{i}"] = False
                        st.rerun()

# Action buttons at bottom
st.divider()
st.markdown("### 🚀 Next Steps")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Update Profile", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

with col2:
    if st.button("🗺️ Create Roadmap", use_container_width=True):
        if filtered_matches:
            st.session_state.selected_role = filtered_matches[0]
        st.switch_page("pages/3_Roadmap.py")

with col3:
    if st.button("🤖 AI Career Coach", use_container_width=True):
        st.switch_page("pages/4_AI_Coach.py")
