import streamlit as st
from core.scoring import skill_gaps
from core import llm
from core.courses import links_for_gap
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.title("🗺️ Your Personalized Learning Roadmap")
st.markdown("### Transform your career with AI-guided learning paths")

matches = st.session_state.get("matches", [])
skills = st.session_state.get("skills", [])
if not matches or not skills:
    st.warning("⚠️ Please find your job matches first to generate a roadmap.")
    if st.button("🎯 Find Job Matches"):
        st.switch_page("pages/2_Matches.py")
    st.stop()

# Initialize progress tracking
if "roadmap_progress" not in st.session_state:
    st.session_state.roadmap_progress = {}

# Role selection and configuration
st.markdown("## 🎯 Choose Your Target Role")

col1, col2 = st.columns([2, 1])

with col1:
    # Check if role was pre-selected from matches page
    default_role = 0
    if st.session_state.get("selected_role"):
        selected_role_name = st.session_state.selected_role["occupation"]
        try:
            default_role = [m["occupation"] for m in matches].index(selected_role_name)
        except ValueError:
            pass
    
    choice = st.selectbox(
        "Select your target role:",
        options=[m["occupation"] for m in matches],
        index=default_role,
        help="Choose the role you want to prepare for"
    )

with col2:
    target = next(m for m in matches if m["occupation"] == choice)
    current_score = int(target['score'] * 100)
    st.metric("Current Match", f"{current_score}%", f"{100-current_score}% to go")

# Skills gap analysis
gaps = skill_gaps(target, skills)
if gaps:
    st.info(f"📚 **Skills to develop for {choice}:** {', '.join(gaps[:3])}{'...' if len(gaps) > 3 else ''}")
else:
    st.success("🎉 **Perfect alignment!** Focus on portfolio building and interview prep.")

st.divider()

# Learning preferences
st.markdown("## ⚙️ Customize Your Learning Experience")

col1, col2 = st.columns(2)

with col1:
    hours_per_week = st.slider("Study hours per week", 1, 25, 8, key="hours")
    timeline_weeks = st.selectbox("Roadmap duration", [4, 6, 8, 12], index=1)

with col2:
    learning_style = st.radio(
        "Preferred learning style",
        ["Video Tutorials", "Reading Documentation", "Project-Based Learning", "Mixed Approach"],
        horizontal=False,
        key="style"
    )

# Generate roadmap
if st.button("🚀 Generate Personalized Roadmap", type="primary"):
    with st.spinner(f"🤖 AI is crafting your {timeline_weeks}-week roadmap..."):
        
        # Enhanced prompt with user preferences
        profile_info = st.session_state.get("user_profile", {})
        context = f"""
        User Profile:
        - Current skills: {skills}
        - Target role: {choice}
        - Skill gaps: {gaps}
        - Experience level: {profile_info.get('experience', 'Unknown')} years
        - Learning style: {learning_style}
        - Study time: {hours_per_week} hours/week
        - Duration: {timeline_weeks} weeks
        """
        
        roadmap = llm.generate_roadmap(
            profile={"skills": skills, "context": context}, 
            target_role=choice, 
            gaps=gaps, 
            hours=hours_per_week, 
            style=learning_style
        )
        st.session_state.roadmap = roadmap
        st.session_state.roadmap_target = choice
        st.session_state.roadmap_config = {
            "hours": hours_per_week,
            "weeks": timeline_weeks,
            "style": learning_style
        }

# Display roadmap with progress tracking
if st.session_state.get("roadmap"):
    st.divider()
    st.markdown("## 📋 Your Learning Roadmap")
    
    # Progress overview
    col1, col2, col3 = st.columns(3)
    
    progress_data = st.session_state.roadmap_progress
    completed_tasks = sum(1 for task_id, completed in progress_data.items() if completed)
    total_tasks = len(progress_data) if progress_data else 6 * 4  # Estimate 4 tasks per week
    
    with col1:
        st.metric("Weeks in Plan", st.session_state.roadmap_config.get("weeks", 6))
    with col2:
        st.metric("Hours/Week", st.session_state.roadmap_config.get("hours", 8))
    with col3:
        completion_rate = (completed_tasks / max(total_tasks, 1)) * 100
        st.metric("Progress", f"{completion_rate:.0f}%")
    
    # Progress bar
    if total_tasks > 0:
        st.progress(completion_rate / 100, text=f"Completed {completed_tasks}/{total_tasks} tasks")
    
    # Roadmap content with checkboxes
    roadmap_lines = st.session_state.roadmap.split('\n')
    current_week = None
    task_counter = 0
    
    for line in roadmap_lines:
        if line.strip().startswith('##') and 'Week' in line:
            current_week = line.strip()
            st.markdown(f"### {current_week.replace('##', '').strip()}")
            
        elif line.strip().startswith('-') or line.strip().startswith('*'):
            task_counter += 1
            task_id = f"task_{task_counter}"
            task_text = line.strip().lstrip('- *').strip()
            
            if task_text:
                col1, col2 = st.columns([1, 10])
                with col1:
                    completed = st.checkbox("", key=task_id, 
                                          value=progress_data.get(task_id, False))
                    progress_data[task_id] = completed
                    st.session_state.roadmap_progress = progress_data
                
                with col2:
                    if completed:
                        st.markdown(f"~~{task_text}~~ ✅")
                    else:
                        st.markdown(task_text)
        else:
            if line.strip():
                st.markdown(line)
    

# Interactive skill modules
if gaps:
    st.divider()
    st.markdown("## 🎓 Learning Resources")
    
    # Show top 3 skill gaps with simple resources
    for i, gap in enumerate(gaps[:3]):
        with st.expander(f"📚 Learn {gap}", expanded=False):
            st.markdown(f"**Essential skill for your {choice} role**")
            
            # Learning resources
            st.markdown("**📖 Recommended Resources:**")
            resource_links = links_for_gap(gap)
            
            cols = st.columns(min(len(resource_links), 3))
            for j, (platform, link) in enumerate(resource_links.items()):
                if j < 3:  # Show only first 3 resources
                    with cols[j]:
                        st.link_button(f"{platform}", link, use_container_width=True)
            
            # Simple practice ideas
            st.markdown("**💪 Practice Ideas:**")
            st.write(f"• Start with basic {gap} tutorials")
            st.write(f"• Build a small project using {gap}")
            st.write(f"• Join {gap} communities for support")

# Career preparation tools
st.divider()
st.markdown("## 🚀 Career Preparation Tools")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📝 Resume Help")
    if st.button("✨ Generate Resume Tips", use_container_width=True):
        with st.spinner("Creating resume guidance..."):
            bullets = llm.generate_resume_bullets(choice, skills, gaps)
            st.session_state.resume_bullets = bullets
    
    if st.session_state.get("resume_bullets"):
        st.markdown("**📋 Resume Tips:**")
        st.markdown(st.session_state.resume_bullets)

with col2:
    st.markdown("### 🎤 Interview Prep")
    if st.button("🎯 Get Interview Questions", use_container_width=True):
        with st.spinner("Preparing interview questions..."):
            questions = llm.generate_interview_questions(choice, skills)
            st.session_state.interview_questions = questions
    
    if st.session_state.get("interview_questions"):
        st.markdown("**🎯 Interview Questions:**")
        st.markdown(st.session_state.interview_questions)

with col3:
    st.markdown("### 🎯 Job Search")
    # Smart job search with user's top skills
    user_skills_set = set(skills)
    required_skills_set = set(s['skill'] for s in target['skills_required'])
    matching_skills = list(user_skills_set.intersection(required_skills_set))
    
    from core.jobs import refined_google_jobs, job_links
    
    smart_link = refined_google_jobs(choice, matching_skills[:3])
    st.link_button("🔍 Smart Job Search", smart_link, use_container_width=True)
    
    regular_links = job_links(choice)
    for platform, link in list(regular_links.items())[:2]:  # Show only 2 platforms
        st.link_button(f"📊 {platform}", link, use_container_width=True)

# Action buttons
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Regenerate Roadmap", use_container_width=True):
        if "roadmap" in st.session_state:
            del st.session_state["roadmap"]
        st.rerun()

with col2:
    if st.button("🎯 Update Target Role", use_container_width=True):
        st.switch_page("pages/2_Matches.py")

with col3:
    if st.button("🤖 Ask AI Coach", use_container_width=True):
        st.switch_page("pages/4_AI_Coach.py")