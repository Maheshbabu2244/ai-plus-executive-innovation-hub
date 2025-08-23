import streamlit as st
import openai
from app import log_activity

st.set_page_config(page_title="AI Mentor Chatbot", layout="wide")

def query_openai_api(system_prompt, user_prompt, api_key):
    openai.api_key = api_key
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API Error: {e}")
    return None

st.title("💬 AI Mentor Chatbot")
st.info("Get advice from different AI executive personas.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in to use this feature.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

persona = st.selectbox("Choose a persona:", ["CEO", "Data Scientist", "HR Head"])

if "mentor_messages" not in st.session_state or st.session_state.get("current_persona") != persona:
    st.session_state.mentor_messages = []
    st.session_state.current_persona = persona
    st.session_state.mentor_messages.append({
        "role": "assistant",
        "content": f"Hello! I am your AI Mentor, speaking as a {persona}. How can I help?"
    })

for message in st.session_state.mentor_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask for advice..."):
    st.session_state.mentor_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            system_prompt = f"""
            You are an AI Mentor for executives. Your persona is a {persona}.
            - As a CEO, focus on strategy, vision, and business impact.
            - As a Data Scientist, focus on technology, data, and implementation.
            - As an HR Head, focus on people, skills, and organizational change.
            """
            response = query_openai_api(system_prompt, prompt, st.session_state.api_key)
            st.markdown(response)
            st.session_state.mentor_messages.append({"role": "assistant", "content": response})
            log_activity(st.session_state.username, "Used AI Mentor", f"Persona: {persona}")
