import streamlit as st
import openai
from app import log_activity

st.set_page_config(page_title="Negotiation & Communication Coach", layout="wide")

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

st.title("🤝 Negotiation & Communication Coach")
st.info("Practice your pitching and negotiation skills in a role-play scenario.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in on the main page.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

persona_role = st.selectbox("Choose the role for the AI to play:", ["Investor", "Partner", "Client"])

if "coach_messages" not in st.session_state or st.session_state.get("current_coach_persona") != persona_role:
    st.session_state.coach_messages = []
    st.session_state.current_coach_persona = persona_role
    st.session_state.coach_messages.append({
        "role": "assistant",
        "content": f"Hello. I will be playing the role of a {persona_role}. Please begin your pitch or negotiation."
    })

for message in st.session_state.coach_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Your pitch/response..."):
    st.session_state.coach_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Get the persona's response
            response_prompt = f"The executive you are talking to just said: \"{prompt}\". Respond realistically to their statement."
            persona_response = query_openai_api(f"You are playing the role of a {persona_role}.", response_prompt, st.session_state.api_key)
            st.markdown(persona_response)
            st.session_state.coach_messages.append({"role": "assistant", "content": persona_response})

            # Get the feedback
            feedback_prompt = f"""
            The executive just said: "{prompt}" to a {persona_role}.
            Provide:
            1. Feedback on my tone, clarity, and persuasiveness
            2. Suggestions to improve my communication
            3. Score out of 10 for effectiveness
            """
            feedback = query_openai_api("You are a communication coach.", feedback_prompt, st.session_state.api_key)
            with st.expander("Show Feedback on Your Last Message"):
                st.info(feedback)
            log_activity(st.session_state.username, "Used Negotiation Coach")
