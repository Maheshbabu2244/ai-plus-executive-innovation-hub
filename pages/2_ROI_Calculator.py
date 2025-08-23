import streamlit as st
import openai
from app import log_activity

st.set_page_config(page_title="Cost-Benefit & ROI Calculator", layout="wide")

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

st.title("🧮 AI Cost-Benefit & ROI Calculator")
st.info("Evaluate the financial viability of a project idea.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

project_idea = st.text_area("Describe the project idea:", height=100, placeholder="Implementing an AI-powered customer support system.")
investment_amount = st.text_input("Enter the estimated investment amount:", placeholder="$200,000")

if st.button("Calculate ROI"):
    if project_idea and investment_amount:
        with st.spinner("Analyzing project..."):
            system_prompt = "You are a financial strategist."
            user_prompt = f"""
            Evaluate the project idea: {project_idea} with an investment of {investment_amount}.
            Provide:
            1. Estimated ROI (%)
            2. Payback period
            3. Key risks
            4. Alternative approaches
            Explain in simple terms suitable for an executive boardroom presentation.
            """
            response = query_openai_api(system_prompt, user_prompt, st.session_state.api_key)
            if response:
                st.markdown(response)
                log_activity(st.session_state.username, "Used ROI Calculator")
    else:
        st.warning("Please fill in both fields.")
