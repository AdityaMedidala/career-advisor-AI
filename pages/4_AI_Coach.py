import streamlit as st
from core.llm import MODEL

st.title("🤖 AI Career Coach")
st.info("Ask me anything about your career goals, skills, or learning roadmap!")

if not st.session_state.get("skills"):
    st.warning("Please create your profile first to activate the AI Coach.")
    if st.button("📝 Create Profile Now"):
        st.switch_page("pages/1_Profile.py")
    st.stop()

if "ai_coach_setup" not in st.session_state:
    profile = st.session_state.get("user_profile", {})
    target_role = "your target role"
    if st.session_state.get("matches"):
        target_role = st.session_state.matches[0]['occupation']
    roadmap = st.session_state.get("roadmap", "No roadmap has been generated yet.")

    system_prompt = f"""
You are "Career Coach", an expert AI career advisor. You are speaking to {profile.get('name', 'a user')}.
Your purpose is to help them achieve their career goals based on their profile.
USER'S CONTEXT:
- TARGET ROLE: {target_role}
- THEIR SKILLS: {st.session_state.get('skills', [])}
- THEIR ROADMAP: {roadmap}

Instructions:
1. Be conversational and encouraging
2. Provide specific, actionable advice
3. Focus on career, skills, and job searching topics
4. Don't repeat their data back to them

Start by introducing yourself and asking how you can help with their career journey.
"""
    st.session_state.chat_session = MODEL.start_chat(history=[])
    with st.spinner("Setting up your AI coach..."):
        st.session_state.chat_session.send_message(system_prompt)
    st.session_state.ai_coach_setup = True
    
if "chat_session" in st.session_state:
    for message in st.session_state.chat_session.history:
        # Filter out the initial system prompt from the displayed history
        if message.role == "user" and "USER'S CONTEXT" in message.parts[0].text:
            continue
        with st.chat_message(message.role):
            st.markdown(message.parts[0].text)

if prompt := st.chat_input("What would you like to discuss?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Thinking..."):
        response = st.session_state.chat_session.send_message(prompt)
    with st.chat_message("model"):
        st.markdown(response.text)

# Quick action buttons
st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Update Profile", use_container_width=True):
        st.switch_page("pages/1_Profile.py")

with col2:
    if st.button("🎯 Find Matches", use_container_width=True):
        st.switch_page("pages/2_Matches.py")

with col3:
    if st.button("🗺️ Create Roadmap", use_container_width=True):
        st.switch_page("pages/3_Roadmap.py")