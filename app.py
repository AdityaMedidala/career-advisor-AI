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
st.title("🎯 Career & Education Advisor")
st.markdown("### Your AI-Powered Career Transformation Platform")

# Hero section with key features
col1, col2, col3 = st.columns(3)
with col1:
    st.info("**🧠 AI-Powered Analysis**\nExtract and analyze your skills from resumes and profiles")

with col2:
    st.success("**🎯 Perfect Job Matching**\nFind roles that align with your skills using intelligent scoring")

with col3:
    st.warning("**🗺️ Personalized Roadmaps**\nGet customized learning plans tailored to your goals")

st.divider()

# Getting Started Guide
st.markdown("## 🚀 How to Get Started")

# Simple 4-step process
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("**1. 📝 Create Profile**\n\nUpload resume or describe your background")
    
with col2:
    st.markdown("**2. 🎯 Find Matches**\n\nDiscover roles that fit your skills")
    
with col3:
    st.markdown("**3. 🗺️ Build Roadmap**\n\nGet personalized learning plans")
    
with col4:
    st.markdown("**4. 🤖 AI Coach**\n\nGet career guidance and support")

st.divider()

# Call to Action
if not st.session_state.get("skills"):
    st.markdown("### 👉 Ready to transform your career?")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Start Your Profile Now", type="primary", use_container_width=True):
            st.switch_page("pages/1_Profile.py")
else:
    st.success("✅ Profile created! Continue your journey:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not st.session_state.get("matches"):
            if st.button("🎯 Find Your Matches", type="primary", use_container_width=True):
                st.switch_page("pages/2_Matches.py")
        else:
            st.success("✅ Matches found!")
    
    with col2:
        if not st.session_state.get("roadmap"):
            if st.button("🗺️ Create Roadmap", type="primary", use_container_width=True):
                st.switch_page("pages/3_Roadmap.py")
        else:
            st.success("✅ Roadmap created!")
    
    with col3:
        if st.button("🤖 Talk to AI Coach", type="primary", use_container_width=True):
            st.switch_page("pages/4_AI_Coach.py")

# Footer
st.markdown("---")
st.caption("🔒 Privacy-First: All processing happens locally. No personal data is stored or transmitted.")