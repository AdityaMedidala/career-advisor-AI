import streamlit as st, pdfplumber
from core import llm
from core.normalize import normalize_skills

st.title("Profile")

def extract_pdf_text(uploaded):
    if uploaded is None: 
        return ""
    try:
        with pdfplumber.open(uploaded) as pdf:
            return "\n".join((p.extract_text() or "") for p in pdf.pages)
    except Exception:
        return ""

# --- use a different form key ---
with st.form(key="profile_form"):
    name = st.text_input("Name")
    exp = st.slider("Years of experience", 0, 30, 2)
    interests = st.multiselect("Interested in", ["Data", "Software", "Cloud", "Security", "Product", "Design"])
    free_text = st.text_area("Background & goals")
    pdf = st.file_uploader("Upload resume (optional, PDF)", type=["pdf"])
    submitted = st.form_submit_button("Analyze Skills")

if submitted:
    text = (extract_pdf_text(pdf) + "\n" + (free_text or "")).strip()
    if not text:
        st.error("Please upload a PDF or add some background text.")
        st.stop()

    skills_raw = llm.extract_skills(text)
    skills = normalize_skills(skills_raw)

    # --- store under a DIFFERENT session_state key ---
    st.session_state.user_profile = {
        "name": name,
        "experience": exp,
        "interests": interests,
        "skills": skills,
    }
    st.session_state.skills = skills

    st.success(f"Extracted {len(skills)} skills. Proceed to Matches →")
    st.write(skills)