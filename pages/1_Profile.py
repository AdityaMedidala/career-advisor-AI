import streamlit as st
from core import llm
from core.resume import get_text
from core.normalize import normalize_skills
import plotly.express as px
import pandas as pd

st.title("📝 Your Professional Profile")
st.markdown("### Build your career profile with AI-powered analysis")

# Profile creation tabs
tab1, tab2 = st.tabs(["📄 Create Profile", "📊 Your Skills"])

with tab1:
    st.markdown("#### Tell us about your professional background")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name (optional)", help="Help us personalize your experience")
            exp = st.slider("Years of experience", 0, 30, 2, help="Include internships and relevant projects")
            current_role = st.text_input("Current/Most Recent Role", placeholder="e.g., Software Developer, Marketing Analyst")
        
        with col2:
            industry = st.selectbox("Industry", [
                "Technology", "Finance", "Healthcare", "Education", "Marketing", 
                "Consulting", "Manufacturing", "Retail", "Government", "Non-profit", "Other"
            ])
            education = st.selectbox("Highest Education Level", [
                "High School", "Some College", "Bachelor's", "Master's", "PhD", "Other"
            ])
        
        career_goals = st.text_area(
            "Career Goals & Aspirations", 
            height=100,
            placeholder="What do you want to achieve in your career? Any specific roles or industries you're targeting?"
        )
        
        free_text = st.text_area(
            "Professional Background & Experience", 
            height=150,
            placeholder="Describe your work experience, projects, achievements, and skills. Or paste your resume text here..."
        )
        
        pdf = st.file_uploader("📎 Upload Resume (PDF)", type=["pdf"], 
                              help="We'll extract your skills and experience automatically")
        
        submitted = st.form_submit_button("🧠 Analyze My Profile with AI", type="primary")

    if submitted:
        text = get_text(pdf, free_text)
        if not text.strip() and not current_role:
            st.error("Please either upload a PDF, enter background text, or at least specify your current role.")
            st.stop()

        # Combine all text for analysis
        analysis_text = f"""
        Name: {name}
        Current Role: {current_role}
        Industry: {industry}
        Experience: {exp} years
        Education: {education}
        Career Goals: {career_goals}
        Background: {text}
        """

        with st.spinner("🤖 AI is analyzing your profile..."):
            raw_skills = llm.extract_skills(analysis_text)
            skills = normalize_skills(raw_skills)

        # Save comprehensive profile
        profile_data = {
            "name": name, 
            "experience": exp, 
            "current_role": current_role,
            "industry": industry,
            "education": education,
            "career_goals": career_goals,
            "skills": skills
        }
        
        st.session_state.user_profile = profile_data
        st.session_state.skills = skills
        
        st.success(f"✅ Profile analyzed! Extracted {len(skills)} skills from your background.")
        
        # Get strategic insights
        with st.spinner("🔍 AI is analyzing your strategic career options..."):
            insights = llm.get_strategic_insights(skills)
            st.session_state.insights = insights

with tab2:
    st.markdown("#### Your Skills Portfolio")
    
    if st.session_state.get("skills"):
        skills = st.session_state.skills
        
        # Skills editing interface
        st.markdown("**📝 Review and Edit Your Skills:**")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            edited_skills = st.multiselect(
                "Your current skills (add/remove as needed):",
                options=sorted(skills + ["Python", "SQL", "JavaScript", "AWS", "Docker", "Git", 
                              "Excel", "Tableau", "React", "Node.js", "Linux", "Agile", "Scrum"]),
                default=skills,
                help="Start typing to add new skills not in the list"
            )
        
        with col2:
            if st.button("🔄 Update Skills"):
                st.session_state.skills = edited_skills
                st.success("Skills updated!")
                st.rerun()
        
        # Simple skills display
        if edited_skills:
            st.markdown("**📊 Your Skills:**")
            
            # Display skills in a clean grid
            cols = st.columns(4)
            for i, skill in enumerate(edited_skills):
                with cols[i % 4]:
                    st.write(f"• {skill}")
        
        # Strategic insights display
        if st.session_state.get("insights"):
            st.markdown("---")
            st.markdown("### 🎯 AI Career Strategy Insights")
            
            with st.container(border=True):
                st.markdown(st.session_state.insights)
    
    else:
        st.info("👆 Complete your profile analysis first to see your skills breakdown.")

# Next steps
if st.session_state.get("skills"):
    st.divider()
    st.markdown("### 🚀 Next Steps")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎯 Find Job Matches", use_container_width=True):
            st.switch_page("pages/2_Matches.py")
    
    with col2:
        if st.button("🗺️ Create Roadmap", use_container_width=True):
            st.switch_page("pages/3_Roadmap.py")
    
    with col3:
        if st.button("📊 Market Insights", use_container_width=True):
            st.switch_page("pages/5_Market_Insights.py")

# Profile summary sidebar
if st.session_state.get("user_profile"):
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Profile Summary")
        profile = st.session_state.user_profile
        
        if profile.get("name"):
            st.write(f"**Name:** {profile['name']}")
        if profile.get("current_role"):
            st.write(f"**Role:** {profile['current_role']}")
        st.write(f"**Experience:** {profile.get('experience', 0)} years")
        
        skill_count = len(st.session_state.get("skills", []))
        st.metric("Skills Identified", skill_count)
        
        if skill_count > 0:
            st.success("✅ Ready for matching!")