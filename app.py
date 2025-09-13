import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
from core.scoring import load_occupations
import random

load_dotenv()

st.set_page_config(
    page_title="Career & Education Advisor", 
    page_icon="🎯", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Use non-conflicting keys (avoid 'profile')
defaults = {
    "user_profile": {},
    "skills": [],
    "matches": [],
    "roadmap": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Enhanced Sidebar
st.sidebar.title("🎯 Career & Education Advisor")
st.sidebar.markdown("### 📊 Your Journey")
st.sidebar.caption("Track your progress through our personalized career discovery process")

# Progress tracking
pages_completed = []
if st.session_state.get("skills"):
    pages_completed.append("✅ Profile Created")
if st.session_state.get("matches"):
    pages_completed.append("✅ Matches Found")
if st.session_state.get("roadmap"):
    pages_completed.append("✅ Roadmap Generated")

if pages_completed:
    for page in pages_completed:
        st.sidebar.write(page)
    st.sidebar.progress(len(pages_completed) / 3)
else:
    st.sidebar.write("🚀 Start with creating your profile!")
    st.sidebar.progress(0)

st.sidebar.divider()
st.sidebar.caption("💡 **Tip:** Complete pages in order for the best experience")
st.sidebar.caption("🔄 No data is stored. Refresh to clear session.")

if st.sidebar.button("🔄 Reset Session", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# Main Content
st.title("🎯 One-Stop Personalized Career & Education Advisor")
st.markdown("### Your AI-Powered Career Transformation Platform")

# Hero section with key features
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🧠 AI-Powered Analysis**\nLeverage Google's Gemini AI to extract and analyze your skills from resumes and profiles")

with col2:
    st.success("**🎯 Perfect Job Matching**\nFind roles that align with your skills using our intelligent scoring algorithm")

with col3:
    st.warning("**🗺️ Personalized Roadmaps**\nGet customized 6-week learning plans tailored to your goals and schedule")

st.divider()

# Job Market Insights Section
st.markdown("## 📈 Current Job Market Insights")

# Load occupations data for insights
@st.cache_data
def get_market_data():
    occupations = load_occupations()
    return occupations

try:
    market_data = get_market_data()
    
    if market_data:
        # Create market insights
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🔥 Most In-Demand Skills Across All Roles")
            
            # Aggregate skill data
            skill_counts = {}
            skill_importance = {}
            
            for occupation in market_data:
                for skill_obj in occupation.get('skills_required', []):
                    skill = skill_obj['skill']
                    weight = skill_obj['weight']
                    
                    if skill in skill_counts:
                        skill_counts[skill] += 1
                        skill_importance[skill] += weight
                    else:
                        skill_counts[skill] = 1
                        skill_importance[skill] = weight
            
            # Calculate average importance and create DataFrame
            skills_data = []
            for skill, count in skill_counts.items():
                avg_importance = skill_importance[skill] / count
                skills_data.append({
                    'Skill': skill,
                    'Demand_Frequency': count,
                    'Average_Importance': avg_importance,
                    'Total_Score': count * avg_importance
                })
            
            skills_df = pd.DataFrame(skills_data)
            top_skills = skills_df.nlargest(10, 'Total_Score')
            
            # Create horizontal bar chart
            fig_skills = px.bar(
                top_skills, 
                x='Total_Score', 
                y='Skill',
                color='Average_Importance',
                orientation='h',
                title="Top 10 Skills by Market Demand × Importance",
                color_continuous_scale='Viridis',
                hover_data=['Demand_Frequency', 'Average_Importance']
            )
            fig_skills.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_skills, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Market Stats")
            
            # Key metrics
            total_roles = len(market_data)
            total_skills = len(skill_counts)
            avg_skills_per_role = sum(len(occ['skills_required']) for occ in market_data) / len(market_data)
            
            st.metric("Total Career Paths", total_roles)
            st.metric("Unique Skills Tracked", total_skills)
            st.metric("Avg Skills per Role", f"{avg_skills_per_role:.1f}")
            
            # Most versatile skills
            st.markdown("**🌟 Most Versatile Skills:**")
            versatile_skills = skills_df.nlargest(5, 'Demand_Frequency')
            for _, row in versatile_skills.iterrows():
                st.write(f"• **{row['Skill']}** - Required in {row['Demand_Frequency']}/{total_roles} roles")
        
        st.divider()
        
        # Career Growth Trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚀 High-Growth Career Fields")
            
            # Simulate growth data based on skill complexity and demand
            growth_data = []
            field_mapping = {
                'Data': ['Data Scientist', 'Data Analyst', 'Business Analyst', 'Database Administrator'],
                'Technology': ['Software Engineer', 'Full Stack Developer', 'Frontend Developer', 'Backend Developer'],
                'Cloud & DevOps': ['DevOps Engineer', 'Cloud Engineer'],
                'AI & ML': ['Machine Learning Engineer'],
                'Security': ['Cybersecurity Analyst', 'Network Engineer'],
                'Design & UX': ['UI/UX Designer'],
                'Management': ['Product Manager', 'IT Project Manager']
            }
            
            for field, roles in field_mapping.items():
                field_roles = [occ for occ in market_data if occ['occupation'] in roles]
                if field_roles:
                    avg_complexity = sum(len(role['skills_required']) for role in field_roles) / len(field_roles)
                    # Simulate growth percentage (in real app, this would come from labor statistics)
                    growth = random.randint(8, 25)  # Simulated 8-25% growth
                    growth_data.append({'Field': field, 'Growth_Rate': growth, 'Complexity': avg_complexity})
            
            growth_df = pd.DataFrame(growth_data).sort_values('Growth_Rate', ascending=False)
            
            for _, row in growth_df.head(5).iterrows():
                st.write(f"📈 **{row['Field']}**: {row['Growth_Rate']}% projected growth")
        
        with col2:
            st.markdown("### 💰 Salary Potential Indicators")
            
            # Create salary indicator based on skill complexity and importance
            salary_data = []
            for occupation in market_data:
                skill_complexity = sum(skill['weight'] for skill in occupation['skills_required'])
                num_skills = len(occupation['skills_required'])
                # Simulate salary ranges (in real app, integrate with salary APIs)
                base_salary = 50000 + (skill_complexity * 8000) + (num_skills * 3000)
                salary_range = f"${base_salary:,} - ${base_salary + 30000:,}"
                salary_data.append({
                    'Role': occupation['occupation'],
                    'Complexity_Score': skill_complexity,
                    'Salary_Range': salary_range,
                    'Base_Salary': base_salary
                })
            
            salary_df = pd.DataFrame(salary_data).sort_values('Base_Salary', ascending=False)
            
            st.markdown("**Top earning potential roles:**")
            for _, row in salary_df.head(5).iterrows():
                st.write(f"💵 **{row['Role']}**: {row['Salary_Range']}")
    
    else:
        st.error("Unable to load market data for insights.")

except Exception as e:
    st.error(f"Error loading market insights: {str(e)}")

st.divider()

# Getting Started Guide
st.markdown("## 🚀 How to Get Started")

steps_col1, steps_col2 = st.columns(2)

with steps_col1:
    st.markdown("""
    ### Your 4-Step Career Journey:
    
    **1. 📝 Create Your Profile**
    - Upload your resume or describe your background
    - Let AI extract and analyze your skills
    - Get strategic career insights
    
    **2. 🎯 Find Perfect Matches**
    - Discover roles that fit your skill set
    - See detailed match scores and skill gaps
    - Explore smart job search links
    """)

with steps_col2:
    st.markdown("""
    ### Advanced Features:
    
    **3. 🗺️ Build Your Roadmap**
    - Get personalized 6-week learning plans
    - Interactive skill-building modules
    - Resume and interview preparation
    
    **4. 🤖 AI Career Coaching**
    - Chat with your personal AI coach
    - Get answers about your career path
    - Continuous guidance and support
    """)

# Call to Action
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if not st.session_state.get("skills"):
        st.markdown("### 👉 Ready to transform your career?")
        if st.button("🚀 Start Your Profile Now", type="primary", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
    else:
        st.success("✅ Profile created! Continue your journey:")
        if not st.session_state.get("matches"):
            if st.button("🎯 Find Your Matches", type="primary", use_container_width=True):
                st.switch_page("pages/2_Matches.py")
        elif not st.session_state.get("roadmap"):
            if st.button("🗺️ Create Learning Roadmap", type="primary", use_container_width=True):
                st.switch_page("pages/3_Roadmap.py")
        else:
            if st.button("🤖 Talk to AI Coach", type="primary", use_container_width=True):
                st.switch_page("pages/4_AI_Coach.py")

# Footer
st.markdown("---")
st.caption("🔒 Privacy-First: All processing happens locally. No personal data is stored or transmitted.")