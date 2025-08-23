import streamlit as st
import openai
from app import log_activity

st.set_page_config(page_title="Business Scenario Simulator", layout="wide")

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

st.title("📈 AI-Powered Business Scenario Simulator")
st.info("Analyze 'What if' scenarios to understand potential business impact.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

scenario = st.text_area("Enter a 'What if' scenario:", height=100, placeholder="What if we cut our marketing budget by 30%?")

if st.button("Analyze Scenario"):
    if scenario:
        with st.spinner("Simulating scenario..."):
            system_prompt = "You are a strategic business advisor."
            user_prompt = f"""
            Analyze the following "What if" scenario: {scenario}.
            Provide:
            1. Financial impact (short & long term)
            2. Risks & challenges
            3. Customer impact
            4. Recommended executive action
            Give the response in a structured format with bullet points.
            """
            response = query_openai_api(system_prompt, user_prompt, st.session_state.api_key)
            if response:
                st.markdown(response)
                log_activity(st.session_state.username, "Used Scenario Simulator")
    else:
        st.warning("Please enter a scenario.")
