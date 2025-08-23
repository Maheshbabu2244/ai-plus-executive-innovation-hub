import streamlit as st
from PyPDF2 import PdfReader
import openai
from app import log_activity

st.set_page_config(page_title="AI Compliance & Ethics Checker", layout="wide")

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

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        return "".join(page.extract_text() for page in reader.pages if page.extract_text())
    else:
        return uploaded_file.getvalue().decode("utf-8")

st.title("📌 AI Compliance & Ethics Checker")
st.info("Review your AI policy drafts against key ethical and regulatory principles.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload your AI policy draft (PDF or TXT):", type=["pdf", "txt"])

if uploaded_file:
    policy_text = extract_text(uploaded_file)

    if st.button("Review Policy"):
        with st.spinner("Reviewing policy..."):
            system_prompt = "You are an AI Ethics Officer."
            user_prompt = f"""
            Review the following company AI policy draft: {policy_text}.
            Check it against the principles of:
            - Fairness
            - Transparency
            - GDPR compliance
            - EU AI Act guidelines

            Provide:
            1. Strengths of this policy
            2. Weaknesses or risks
            3. Recommendations to improve
            Use clear and concise business language.
            """
            response = query_openai_api(system_prompt, user_prompt, st.session_state.api_key)
            if response:
                st.markdown(response)
                log_activity(st.session_state.username, "Used Compliance Checker")
