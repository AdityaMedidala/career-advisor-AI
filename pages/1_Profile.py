import streamlit as st
from core import llm
from core.resume import get_text
from core.normalize import normalize_skills

st.title("Profile")

with st.form("profile"):
    name = st.text_input("Name (optional)")
    exp = st.slider("Years of experience", 0, 30, 2)
    interests = st.multiselect(
        "Interests",
        ["Data", "Software", "Cloud", "Security", "Product", "Design", "AI/ML", "DevOps"]
    )
    free_text = st.text_area("Tell us about your background & goals", height=150,
                             placeholder="Paste your summary or resume text here...")
    pdf = st.file_uploader("Upload resume (optional, PDF only)", type=["pdf"])
    submitted = st.form_submit_button("Analyze my skills with Gemini")

if submitted:
    text = get_text(pdf, free_text)
    if not text.strip():
        st.error("Please upload a PDF or enter some background text.")
        st.stop()
    raw_skills = llm.extract_skills(text)
    skills = normalize_skills(raw_skills)
    st.session_state.profile = {"name": name, "experience": exp, "interests": interests, "skills": skills}
    st.session_state.skills = skills
    st.success(f"Extracted {len(skills)} skills. Go to **Matches** →")
    st.write(skills)
