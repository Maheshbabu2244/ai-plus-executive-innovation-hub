import streamlit as st
import pandas as pd
import os
import re
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFil  
from PIL import Image                                                   
from app import log_activity

st.set_page_config(page_title="AI+ Executive Innovation Hub", page_icon="🚀", layout="wide")

# Directory for user analytics
DATA_DIR = "user_data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_user_data_file(username, data_type="analytics"):
    sanitized_username = re.sub(r'[^a-zA-Z0-9_]', '', username.lower())
    return os.path.join(DATA_DIR, f"{sanitized_username}_{data_type}.csv")

def log_activity(username, activity, details=""):
    analytics_file = get_user_data_file(username, "analytics")
    if os.path.exists(analytics_file):
        df = pd.read_csv(analytics_file)
    else:
        df = pd.DataFrame(columns=["timestamp", "activity", "details"])
    new_log = pd.DataFrame({
        "timestamp": [pd.Timestamp.now()], "activity": [activity], "details": [details]
    })
    df = pd.concat([df, new_log], ignore_index=True)
    df.to_csv(analytics_file, index=False)

def main():
    # Load API key securely
    st.session_state.api_key = st.secrets.get("OPENAI_API_KEY", "")

    if 'username' not in st.session_state:
        st.session_state.username = ""

    if not st.session_state.username:
        st.title("Welcome to the AI+ Executive Innovation Hub 🚀")
        st.subheader("Your AI-powered toolkit for strategic decision-making.")
        name = st.text_input("Please enter your name to begin:")
        if name:
            st.session_state.username = name
            st.rerun()
        return

    st.sidebar.title(f"Welcome, {st.session_state.username}!")
    st.sidebar.markdown("---")

    # API key validation
    if not st.session_state.api_key:
        st.sidebar.error("❌ OpenAI API Key not found. Please add it to your app's secrets.")
    else:
        st.sidebar.success("✅ OpenAI API Key loaded securely!")

    st.sidebar.markdown("---")
    st.title("🚀 AI+ Executive Innovation Hub")
    st.write("Select a tool from the sidebar to begin.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📊 Strategy & Finance")
        st.write("- Business Scenario Simulator")
        st.write("- Cost-Benefit & ROI Calculator")
        st.write("- AI Trend Radar")
    with col2:
        st.subheader("📝 Content & Learning")
        st.write("- Text-to-Video Generator")
        st.write("- AI Document Q&A")
        st.write("- Quiz Generator")
        st.write("- AI Voice Narrator")
    with col3:
        st.subheader("🧑‍💻 People & Governance")
        st.write("- AI Mentor Chatbot")
        st.write("- AI Compliance & Ethics Checker")
        st.write("- Skill Gap Analyzer")
        st.write("- Negotiation & Communication Coach")

    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

if __name__ == "__main__":
    main()
