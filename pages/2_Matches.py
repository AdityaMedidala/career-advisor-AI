import streamlit as st
from core.scoring import load_occupations, rank_roles
from core.jobs import job_links

st.title("Matches")

skills = st.session_state.get("skills", [])
if not skills:
    st.warning("Add your profile first on the **Profile** page.")
    st.stop()

occs = load_occupations()
matches = rank_roles(skills, occs, top_k=5)
st.session_state.matches = matches

for m in matches:
    with st.expander(f"{m['occupation']} — score {m['score']:.2f}"):
        st.write("**Required skills:**", ", ".join(m["skills_required"]))
        st.write("**Your gaps:**", ", ".join(m["gaps"]) if m["gaps"] else "None 🎉")
        links = job_links(m["occupation"])
        cols = st.columns(len(links))
        for i, (label, url) in enumerate(links.items()):
            with cols[i]:
                st.link_button(label, url, use_container_width=True)
