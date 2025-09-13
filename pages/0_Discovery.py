import streamlit as st
from core import llm

st.title("✨ AI Career Discovery Agent")
st.info("Don't have a target role in mind? Let our AI agent analyze your skills and discover the best career paths for you.")

# Use skills from the profile page if available, or allow new input
skills_list = st.session_state.get("skills", [])
skills_input = st.text_area(
    "Your skills (automatically populated from your profile, or enter comma-separated skills here)",
    value=", ".join(skills_list),
    height=150,
    help="Example: Python, SQL, Git, Data Analysis, APIs"
)

if st.button("Activate Discovery Agent", type="primary"):
    if not skills_input.strip():
        st.error("Please enter at least one skill.")
    else:
        user_skills = [s.strip() for s in skills_input.split(",")]
        with st.spinner("AI Agent is analyzing, hypothesizing, and scoring potential careers... This may take a moment."):
            report = llm.run_career_discovery_agent(user_skills)
            st.session_state.discovery_report = report

if "discovery_report" in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state.discovery_report)