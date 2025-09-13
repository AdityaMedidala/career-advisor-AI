import streamlit as st
from dotenv import load_dotenv; load_dotenv()

st.set_page_config(
    page_title="One-Stop Career & Education Advisor",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state (no DB, nothing is persisted)
for key, default in {
    "profile": {},
    "skills": [],
    "matches": [],
    "roadmap": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.sidebar.title("🎯 Career & Education Advisor")
st.sidebar.caption("No data is stored. Refresh to clear session.")
if st.sidebar.button("Reset session"):
    st.session_state.clear()
    st.rerun()

st.title("One-Stop Personalized Career & Education Advisor")
st.write("Go through **Profile → Matches → Roadmap** using the left sidebar.")
st.info("This demo uses **Gemini** for skill extraction & roadmap generation and keeps all data in session memory only.")