import streamlit as st
import openai
from app import log_activity

st.set_page_config(page_title="AI Trend Radar", layout="wide")

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
        st.error(f"OpenAI API Request Error: {e}")
        return None

st.title("🔮 AI Trend Radar")
st.info("Get a summary of the latest AI innovations relevant to business executives.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

if st.button("Generate Trend Report"):
    with st.spinner("Scanning the horizon for AI trends..."):
        system_prompt = "You are a technology trend analyst."
        user_prompt = """
        Summarize the 5 most important AI innovations in the past 12 months that business executives should know about.
        For each innovation, include:
        - Description in simple terms
        - Example application in business
        - Potential risk or limitation
        Present as a timeline or bullet list.
        """
        response = query_openai_api(system_prompt, user_prompt, st.session_state.api_key)
        if response:
            st.markdown(response)
            log_activity(st.session_state.username, "Used AI Trend Radar")
