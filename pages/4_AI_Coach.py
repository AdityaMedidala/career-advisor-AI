import streamlit as st
from core.llm import MODEL

st.title("🤖 AI Career Co-Pilot")
st.info("Ask me anything about your roadmap, skill gaps, or career goals!")

if "profile" not in st.session_state or not st.session_state.profile.get("skills"):
    st.warning("Please create your profile on the '1. Your Profile' page to activate the AI Coach.")
    st.stop()

if "ai_coach_setup" not in st.session_state:
    profile = st.session_state.profile
    target_role = "your target role"
    if st.session_state.get("matches"):
        target_role = st.session_state.matches[0]['occupation']
    roadmap = st.session_state.get("roadmap", "No roadmap has been generated yet.")

    system_prompt = f"""
You are "Career Co-Pilot", an expert AI career coach. You are speaking to {profile.get('name', 'a user')}.
Your sole purpose is to help them achieve their career goals based on the information they've provided.
HERE IS THE USER'S CONTEXT:
- TARGET ROLE: {target_role}
- THEIR SKILLS: {profile.get('skills', [])}
- THEIR 6-WEEK ROADMAP:
---
{roadmap}
---
Your instructions:
1.  Acknowledge the Context: Do not repeat the user's data back to them. Use it to inform your answers.
2.  Be Conversational and Encouraging: Act as a supportive mentor.
3.  Be Actionable: Provide specific, helpful advice.
4.  Stay on Topic: Gently decline requests that are not related to career, skills, or job searching.
Begin the conversation by introducing yourself and asking how you can help them with their generated plan or career path.
"""
    st.session_state.chat_session = MODEL.start_chat(history=[])
    with st.spinner("Co-Pilot is preparing your session..."):
        st.session_state.chat_session.send_message(system_prompt)
    st.session_state.ai_coach_setup = True
    
if "chat_session" in st.session_state:
    for message in st.session_state.chat_session.history:
        # Filter out the initial system prompt from the displayed history
        if message.role == "user" and "HERE IS THE USER'S CONTEXT" in message.parts[0].text:
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