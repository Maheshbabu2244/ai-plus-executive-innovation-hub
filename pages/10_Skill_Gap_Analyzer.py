import streamlit as st
import pandas as pd
import openai
from app import log_activity

st.set_page_config(page_title="Skill Gap Analyzer", layout="wide")

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

st.title("🧑‍💻 Skill Gap Analyzer")
st.info("Analyze employee skills data to identify AI-related training needs.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

uploaded_file = st.file_uploader("Upload a CSV with employee roles and skills:", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Data Preview:", df.head())

    if st.button("Analyze Skill Gaps"):
        skills_data = df.to_string()
        with st.spinner("Analyzing skills data..."):
            system_prompt = "You are an AI HR consultant."
            user_prompt = f"""
            Based on the following roles and skills data: {skills_data},
            1. Identify missing AI-related skills for each department.
            2. Suggest specific training programs to bridge the gap.
            3. Create a summary heatmap of department readiness for AI adoption (High, Medium, Low).
            Present the result in a structured table format.
            """
            response = query_openai_api(system_prompt, user_prompt, st.session_state.api_key)
            if response:
                st.markdown(response)
                log_activity(st.session_state.username, "Used Skill Gap Analyzer")
