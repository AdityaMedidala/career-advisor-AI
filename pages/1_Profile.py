import streamlit as st
from core import llm
from core.resume import get_text
from core.normalize import normalize_skills
import plotly.express as px
import pandas as pd

st.title("1. 📝 Your Professional Profile")
st.markdown("### Build your comprehensive career profile with AI-powered analysis")

# Profile creation tabs
tab1, tab2, tab3 = st.tabs(["📄 Resume & Background", "🎯 Career Preferences", "📊 Skills Analysis"])

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
            location_pref = st.selectbox("Work Location Preference", [
                "Remote", "Hybrid", "On-site", "No preference"
            ])
            education = st.selectbox("Highest Education Level", [
                "High School", "Some College", "Bachelor's", "Master's", "PhD", "Other"
            ])
        
        interests = st.multiselect(
            "Career Interest Areas (select all that apply)",
            ["Data & Analytics", "Software Development", "Cloud & Infrastructure", 
             "Cybersecurity", "Product Management", "Design & UX", "AI/ML", 
             "DevOps", "Project Management", "Business Analysis", "Marketing", "Sales"]
        )
        
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
            "location_pref": location_pref,
            "interests": interests,
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
    st.markdown("#### Fine-tune your career preferences")
    
    if st.session_state.get("user_profile"):
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Work Preferences**")
            work_style = st.radio("Preferred Work Style", 
                                ["Individual contributor", "Team collaboration", "Leadership role", "Mix of both"])
            
            company_size = st.selectbox("Company Size Preference", 
                                      ["Startup (1-50)", "Small (51-200)", "Medium (201-1000)", 
                                       "Large (1000+)", "No preference"])
            
            learning_style = st.selectbox("Learning Style", 
                                        ["Hands-on projects", "Structured courses", "Mentorship", 
                                         "Self-directed", "Mixed approach"])
        
        with col2:
            st.markdown("**Career Priorities**")
            priorities = st.multiselect("What matters most to you?", 
                                      ["High salary", "Work-life balance", "Career growth", 
                                       "Job security", "Challenging work", "Remote flexibility", 
                                       "Company culture", "Learning opportunities"])
            
            time_commitment = st.slider("Hours per week for skill development", 1, 20, 5)
            
            risk_tolerance = st.select_slider("Career Change Risk Tolerance", 
                                            ["Conservative", "Moderate", "Aggressive"])
        
        # Update profile with preferences
        if st.button("💾 Save Preferences"):
            profile.update({
                "work_style": work_style,
                "company_size": company_size,
                "learning_style": learning_style,
                "priorities": priorities,
                "time_commitment": time_commitment,
                "risk_tolerance": risk_tolerance
            })
            st.session_state.user_profile = profile
            st.success("Preferences saved! This will help personalize your recommendations.")
    
    else:
        st.info("👆 Complete your basic profile first to access career preferences.")

with tab3:
    if st.session_state.get("skills"):
        st.markdown("#### Your Skills Portfolio")
        
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
        
        # Skills visualization
        if edited_skills:
            st.markdown("**📊 Your Skills Breakdown:**")
            
            # Categorize skills (simplified)
            categories = {
                'Programming': ['Python', 'Java', 'JavaScript', 'SQL', 'R', 'C++', 'C#', 'PHP'],
                'Data & Analytics': ['SQL', 'Excel', 'Tableau', 'Power BI', 'Statistics', 'Data Analysis'],
                'Cloud & DevOps': ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform', 'CI/CD'],
                'Web Development': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue.js'],
                'Tools & Platforms': ['Git', 'Jira', 'Linux', 'Windows', 'Slack', 'Confluence'],
                'Soft Skills': ['Communication', 'Leadership', 'Project Management', 'Problem-solving']
            }
            
            skill_categories = {}
            for skill in edited_skills:
                categorized = False
                for category, cat_skills in categories.items():
                    if any(cat_skill.lower() in skill.lower() or skill.lower() in cat_skill.lower() 
                          for cat_skill in cat_skills):
                        if category not in skill_categories:
                            skill_categories[category] = []
                        skill_categories[category].append(skill)
                        categorized = True
                        break
                if not categorized:
                    if 'Other' not in skill_categories:
                        skill_categories['Other'] = []
                    skill_categories['Other'].append(skill)
            
            # Create pie chart
            if skill_categories:
                df = pd.DataFrame([(cat, len(skills)) for cat, skills in skill_categories.items()], 
                                columns=['Category', 'Count'])
                
                fig = px.pie(df, values='Count', names='Category', 
                           title="Your Skills by Category")
                st.plotly_chart(fig, use_container_width=True)
            
            # Skills by category
            col1, col2 = st.columns(2)
            for i, (category, cat_skills) in enumerate(skill_categories.items()):
                with col1 if i % 2 == 0 else col2:
                    with st.expander(f"**{category}** ({len(cat_skills)} skills)"):
                        for skill in cat_skills:
                            st.write(f"• {skill}")
        
        # Strategic insights display
        if st.session_state.get("insights"):
            st.markdown("---")
            st.markdown("### 🎯 AI Career Strategy Insights")
            
            with st.container(border=True):
                st.markdown(st.session_state.insights)
        
        # Next steps
        st.markdown("---")
        st.markdown("### 🚀 Next Steps")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔍 Discover Career Paths", use_container_width=True):
                st.switch_page("pages/0_Discovery.py")
        
        with col2:
            if st.button("🎯 Find Job Matches", use_container_width=True):
                st.switch_page("pages/2_Matches.py")
        
        with col3:
            if st.button("📊 Market Insights", use_container_width=True):
                st.switch_page("pages/5_Market_Insights.py")
    
    else:
        st.info("👆 Complete your profile analysis first to see your skills breakdown.")

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
        if profile.get("industry"):
            st.write(f"**Industry:** {profile['industry']}")
        
        skill_count = len(st.session_state.get("skills", []))
        st.metric("Skills Identified", skill_count)
        
        if skill_count > 0:
            st.success("✅ Ready for matching!")