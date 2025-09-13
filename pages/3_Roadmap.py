import streamlit as st
from core.scoring import skill_gaps
from core import llm
from core.courses import links_for_gap
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

st.title("3. 🗺️ Your Personalized Learning Roadmap")
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

col1, col2, col3 = st.columns(3)

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

with col3:
    difficulty_level = st.selectbox("Starting difficulty", ["Beginner", "Intermediate", "Advanced"])
    focus_area = st.selectbox("Primary focus", ["Technical Skills", "Portfolio Projects", "Interview Prep", "Balanced"])

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
        - Difficulty: {difficulty_level}
        - Focus: {focus_area}
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
            "style": learning_style,
            "difficulty": difficulty_level,
            "focus": focus_area
        }

# Display roadmap with progress tracking
if st.session_state.get("roadmap"):
    st.divider()
    st.markdown("## 📋 Your Learning Roadmap")
    
    # Progress overview
    col1, col2, col3, col4 = st.columns(4)
    
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
    with col4:
        estimated_completion = datetime.now() + timedelta(weeks=st.session_state.roadmap_config.get("weeks", 6))
        st.metric("Target Date", estimated_completion.strftime("%b %d"))
    
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
    
    # Roadmap analytics
    if st.expander("📊 Learning Analytics", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Skills development timeline
            if gaps:
                weeks_data = []
                for i in range(1, st.session_state.roadmap_config.get("weeks", 6) + 1):
                    skills_this_week = min(2, len(gaps))  # Assume 2 skills per week
                    weeks_data.append({
                        'Week': f'Week {i}',
                        'Cumulative_Skills': min(i * 2, len(gaps)),
                        'New_Skills': skills_this_week if i * 2 <= len(gaps) else max(0, len(gaps) - (i-1) * 2)
                    })
                
                df = pd.DataFrame(weeks_data)
                fig = px.bar(df, x='Week', y='New_Skills', 
                           title="Skills Development Timeline")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Time allocation
            time_allocation = {
                'Learning': 60,
                'Practice': 25,
                'Portfolio': 10,
                'Job Prep': 5
            }
            
            fig_pie = px.pie(values=list(time_allocation.values()), 
                           names=list(time_allocation.keys()),
                           title="Recommended Time Allocation")
            st.plotly_chart(fig_pie, use_container_width=True)

# Interactive skill modules
if gaps:
    st.divider()
    st.markdown("## 🎓 Interactive Learning Modules")
    
    # Skill selection tabs
    skill_tabs = st.tabs([f"📚 {gap}" for gap in gaps[:4]])  # Limit to 4 tabs
    
    for i, gap in enumerate(gaps[:4]):
        with skill_tabs[i]:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### Master {gap}")
                st.write(f"Essential skill for your {choice} role")
            
            with col2:
                if st.button(f"🚀 Start Learning", key=f"start_{gap}"):
                    with st.spinner(f"Generating learning module for {gap}..."):
                        module_content = llm.generate_learning_module(gap)
                        st.session_state[f"module_{gap}"] = module_content
            
            # Display module content
            if st.session_state.get(f"module_{gap}"):
                st.markdown("---")
                st.markdown(st.session_state[f"module_{gap}"])
                
                # Learning resources
                st.markdown("**📖 Additional Resources:**")
                resource_links = links_for_gap(gap)
                
                cols = st.columns(len(resource_links))
                for j, (platform, link) in enumerate(resource_links.items()):
                    with cols[j]:
                        st.link_button(f"{platform}", link, use_container_width=True)
                
                # Practice exercises
                with st.expander("💪 Practice Exercises"):
                    st.markdown(f"""
                    **Quick Practice Ideas for {gap}:**
                    
                    1. **15-minute daily challenge**: Look up basic {gap} concepts and terminology
                    2. **Weekend project**: Build a small project using {gap}
                    3. **Community engagement**: Join {gap} communities or forums
                    4. **Documentation**: Create notes or a blog post about what you learn
                    
                    **Track your progress:**
                    """)
                    
                    practice_progress = st.slider(
                        f"How comfortable are you with {gap}? (1-10)", 
                        1, 10, 1, 
                        key=f"practice_{gap}"
                    )
                    
                    if practice_progress >= 7:
                        st.success("🎉 Great progress! You're becoming proficient!")
                    elif practice_progress >= 4:
                        st.info("👍 Good progress! Keep practicing!")
                    else:
                        st.warning("💪 Keep going! Practice makes perfect!")

# Career preparation tools
st.divider()
st.markdown("## 🚀 Career Preparation Toolkit")

toolkit_tab1, toolkit_tab2, toolkit_tab3 = st.tabs(["📝 Resume Optimizer", "🎤 Interview Prep", "🎯 Job Search"])

with toolkit_tab1:
    st.markdown("### AI-Powered Resume Enhancement")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ Generate Resume Bullets", use_container_width=True):
            with st.spinner("Writing powerful resume bullet points..."):
                bullets = llm.generate_resume_bullets(choice, skills, gaps)
                st.session_state.resume_bullets = bullets
    
    with col2:
        if st.button("🔍 Skills Gap Bridge", use_container_width=True):
            with st.spinner("Creating gap-bridging strategies..."):
                # Generate content to help bridge skill gaps in resume
                gap_strategy = f"""
                ## 🌉 Bridging Your Skill Gaps
                
                **For {choice} role, highlight these strategies:**
                
                {''.join([f'- **{gap}**: Emphasize related experience and show learning initiative' for gap in gaps[:3]])}
                
                **Powerful phrases to use:**
                - "Self-directed learning in..."
                - "Currently developing expertise in..."
                - "Applied foundational knowledge of..."
                - "Eager to expand skills in..."
                """
                st.session_state.gap_bridge_strategy = gap_strategy
    
    # Display generated content
    if st.session_state.get("resume_bullets"):
        st.markdown("**📋 Generated Resume Bullet Points:**")
        st.markdown(st.session_state.resume_bullets)
        
    if st.session_state.get("gap_bridge_strategy"):
        st.markdown(st.session_state.gap_bridge_strategy)

with toolkit_tab2:
    st.markdown("### Interview Preparation")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Generate Interview Questions", use_container_width=True):
            with st.spinner("Preparing interview questions..."):
                questions = llm.generate_interview_questions(choice, skills)
                st.session_state.interview_questions = questions
    
    with col2:
        if st.button("💡 STAR Method Examples", use_container_width=True):
            star_examples = f"""
            ## 🌟 STAR Method Framework
            
            **For {choice} interviews, prepare these scenarios:**
            
            **Situation-Task-Action-Result structure for:**
            
            1. **Technical Problem Solving** - Describe a complex problem you solved
            2. **Learning New Technology** - How you quickly mastered a new skill
            3. **Team Collaboration** - Working effectively with diverse teams
            4. **Project Management** - Leading or contributing to successful projects
            
            **Your strengths to highlight:** {', '.join(skills[:5])}
            """
            st.session_state.star_examples = star_examples
    
    if st.session_state.get("interview_questions"):
        st.markdown(st.session_state.interview_questions)
    
    if st.session_state.get("star_examples"):
        st.markdown(st.session_state.star_examples)

with toolkit_tab3:
    st.markdown("### Strategic Job Search")
    
    # Smart job search with user's top skills
    user_skills_set = set(skills)
    required_skills_set = set(s['skill'] for s in target['skills_required'])
    matching_skills = list(user_skills_set.intersection(required_skills_set))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Targeted Job Search:**")
        from core.jobs import refined_google_jobs, job_links
        
        smart_link = refined_google_jobs(choice, matching_skills[:3])
        st.link_button("🎯 Smart Google Jobs Search", smart_link, use_container_width=True)
        
        regular_links = job_links(choice)
        for platform, link in regular_links.items():
            st.link_button(f"📊 {platform}", link, use_container_width=True)
    
    with col2:
        st.markdown("**📈 Job Search Strategy:**")
        st.info(f"""
        **Your competitive advantage:**
        - Strong in: {', '.join(matching_skills[:3])}
        - Developing: {', '.join(gaps[:2]) if gaps else 'Portfolio projects'}
        
        **Search keywords to use:**
        "{choice} {' '.join(matching_skills[:2])}"
        
        **Applications per week target:** 5-10
        **Response rate goal:** 10-20%
        """)

# Action buttons
st.divider()
col1, col2, col3, col4 = st.columns(4)

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

with col4:
    if st.button("📊 View Progress", use_container_width=True):
        # Create a simple progress report
        total_progress = len([k for k, v in st.session_state.roadmap_progress.items() if v])
        st.balloons()
        st.success(f"🎉 You've completed {total_progress} learning tasks! Keep going!")