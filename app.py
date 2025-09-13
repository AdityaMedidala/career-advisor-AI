import streamlit as st
from dotenv import load_dotenv; load_dotenv()

st.set_page_config(page_title="Career & Education Advisor", page_icon="🎯", layout="wide")

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

st.sidebar.title("🎯 Career & Education Advisor")
st.sidebar.caption("No data is stored. Refresh to clear session.")
if st.sidebar.button("Reset session"):
    st.session_state.clear()
    st.rerun()

st.title("One-Stop Personalized Career & Education Advisor")
st.write("Use the pages on the left: **Profile → Matches → Roadmap**")