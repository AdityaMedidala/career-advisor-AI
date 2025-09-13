import streamlit as st
from core.scoring import load_occupations, rank_roles
from core import jobs
from core import llm

st.title("2. Job Matches")

skills = st.session_state.get("skills", [])
if not skills:
    st.warning("Please create a profile or run the Discovery Agent first.")
    st.stop()

st.subheader("Your Skills Profile")
edited_skills = st.multiselect(
    "Add or remove skills below to refine your matches:",
    options=sorted(list(set(skills))),
    default=skills
)
st.session_state.skills = edited_skills
st.divider()

occs = load_occupations()
matches = rank_roles(edited_skills, occs, top_k=5)
st.session_state.matches = matches

st.subheader("Top 5 Role Matches")
for m in matches:
    score_percentage = int(m['score'] * 100)

    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.subheader(m['occupation'])
        with col2:
            st.metric(label="Match Score", value=f"{score_percentage}%")

        st.progress(score_percentage, text=f"{score_percentage}% Skill Alignment")

        if m["gaps"]:
            st.write("**Skill Gaps:**")
            gaps_html = "".join(f'<span style="background-color: #FFD2D2; color: #D8000C; border-radius: 5px; padding: 3px 8px; margin: 2px;">{gap}</span>' for gap in m["gaps"])
            st.markdown(f"<div>{gaps_html}</div>", unsafe_allow_html=True)
        else:
            st.success("🎉 No skill gaps found!")

        with st.expander("Explore & Analyze This Role"):
            user_skills_set = set(edited_skills)
            required_skills_set = set(s['skill'] for s in m["skills_required"])
            matching_user_skills = list(user_skills_set.intersection(required_skills_set))
            smart_link = jobs.refined_google_jobs(m["occupation"], matching_user_skills)
            st.link_button("⭐ Smart Job Search (Google)", smart_link, use_container_width=True)

            st.divider()
            st.write("🔍 **Analyze In-Demand Skills**")
            if st.button(f"Find current top skills for {m['occupation']}", key=m['occupation']):
                with st.spinner("Asking Gemini for the latest market skills..."):
                    st.session_state[f"suggested_{m['occupation']}"] = llm.suggest_skills_for_role(m['occupation'])
            
            suggested_key = f"suggested_{m['occupation']}"
            if suggested_key in st.session_state:
                suggested = st.session_state[suggested_key]
                st.info("Add these skills to your profile below to see how your match score improves!")
                skills_to_add = st.multiselect("Select skills to add:", options=suggested, key=f"multiselect_{m['occupation']}")
                if st.button("Add to My Skills & Rematch", key=f"add_{m['occupation']}"):
                    current_skills = set(st.session_state.skills)
                    current_skills.update(skills_to_add)
                    st.session_state.skills = sorted(list(current_skills))
                    del st.session_state[suggested_key]
                    st.rerun()