import streamlit as st
from core.scoring import skill_gaps
from core import llm
from core.courses import links_for_gap

st.title("Roadmap")

matches = st.session_state.get("matches", [])
skills = st.session_state.get("skills", [])
if not matches or not skills:
    st.warning("Find matches first on the **Matches** page.")
    st.stop()

choice = st.selectbox("Target role", [m["occupation"] for m in matches])
target = next(m for m in matches if m["occupation"] == choice)
gaps = skill_gaps(target, skills)

st.write("**Skill gaps to focus on:**", ", ".join(gaps) if gaps else "None (polish and build portfolio)")

if st.button("Generate roadmap with Gemini"):
    roadmap = llm.generate_roadmap({"skills": skills}, target["occupation"], gaps)
    st.session_state.roadmap = roadmap

if st.session_state.get("roadmap"):
    st.markdown(st.session_state.roadmap)
    # Course links per gap (optional but handy)
    if gaps:
        st.subheader("Suggested learning links")
        for g in gaps:
            st.markdown(f"- **{g}**")
            links = links_for_gap(g)
            st.write("  ", " • ".join(f"[{k}]({v})" for k, v in links.items()))
    md = st.session_state.roadmap.encode("utf-8")
    st.download_button("Download roadmap.md", data=md, file_name=f"{choice}_roadmap.md", mime="text/markdown")
