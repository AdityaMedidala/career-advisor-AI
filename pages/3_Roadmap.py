import streamlit as st
from core.scoring import skill_gaps
from core import llm
from core.courses import links_for_gap

st.title("3. Learning & Career Roadmap")

matches = st.session_state.get("matches", [])
skills = st.session_state.get("skills", [])
if not matches or not skills:
    st.warning("Find your job matches on the '2. Matches' page first.")
    st.stop()

choice = st.selectbox("Select a target role to generate a roadmap:", [m["occupation"] for m in matches])
target = next(m for m in matches if m["occupation"] == choice)
gaps = skill_gaps(target, skills)

st.write(f"**Skill gaps for {choice}:**", ", ".join(gaps) if gaps else "None (focus on portfolio building!)")
st.divider()

st.subheader("Personalized Learning Roadmap")
hours_per_week = st.slider("How many hours per week can you study?", 1, 20, 8, key="hours")
learning_style = st.radio("What is your preferred learning style?", ["Video Tutorials", "Reading Documentation", "Project-Based Learning"], horizontal=True, key="style")
if st.button("Generate 6-Week Learning Plan"):
    with st.spinner("Gemini is crafting your personalized roadmap... 🗺️"):
        roadmap = llm.generate_roadmap(profile={"skills": skills}, target_role=target["occupation"], gaps=gaps, hours=hours_per_week, style=learning_style)
        st.session_state.roadmap = roadmap

if st.session_state.get("roadmap"):
    st.markdown(st.session_state.roadmap)

if gaps:
    st.divider()
    st.subheader("Interactive Learning Modules")
    st.info("Bridge your skill gaps by generating a 'Day 1' micro-lesson for any skill.")

    for gap in gaps:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Skill Gap:** {gap}")
        with col2:
            if st.button(f"Teach Me {gap}", key=f"learn_{gap}", use_container_width=True):
                with st.spinner(f"Generating your learning module for {gap}..."):
                    module_content = llm.generate_learning_module(gap)
                    st.session_state[f"module_{gap}"] = module_content
        
        if f"module_{gap}" in st.session_state:
            with st.container(border=True):
                st.markdown(st.session_state[f"module_{gap}"])

st.divider()
st.subheader("🚀 Career Co-Pilot")
col1, col2 = st.columns(2)
with col1:
    st.info("**Resume Power-Up**")
    if st.button("Generate Resume Bullet Points"):
        with st.spinner("Writing resume phrases..."):
            bullets = llm.generate_resume_bullets(target["occupation"], skills, gaps)
            st.session_state.bullets = bullets
    if "bullets" in st.session_state:
        st.markdown(st.session_state.bullets)
with col2:
    st.info("**Mock Interview Prep**")
    if st.button("Generate Interview Questions"):
        with st.spinner("Preparing questions..."):
            questions = llm.generate_interview_questions(target["occupation"], skills)
            st.session_state.questions = questions
    if "questions" in st.session_state:
        st.markdown(st.session_state.questions)