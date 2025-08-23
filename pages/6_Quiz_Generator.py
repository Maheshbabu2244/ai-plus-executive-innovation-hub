import streamlit as st
import openai
import json
import re
import time
from app import log_activity

st.set_page_config(page_title="Quiz Generator", layout="wide")

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

def generate_quiz(topic, num_questions, api_key):
    system_prompt = "You are an expert quiz designer."
    user_prompt = f"""
    Generate {num_questions} multiple-choice questions on '{topic}'.
    For each, provide: 'question', a list of 'options', the 'correct_answer', and a brief 'explanation'.
    Return as a valid JSON list of dictionaries. Example:
    [
        {{"question": "...", "options": ["A", "B", "C"], "correct_answer": "B", "explanation": "..."}}
    ]
    """
    response_text = query_openai_api(system_prompt, user_prompt, api_key)
    if response_text:
        try:
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            return json.loads(json_match.group(0))
        except (AttributeError, json.JSONDecodeError):
            st.error("Failed to parse quiz.")
    return None

st.title("🧠 Quiz Generator")
st.info("Generate a quiz from any topic.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in to use this feature.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

topic = st.text_input("Enter a topic for your quiz:")
num_questions = st.slider("Number of questions:", 1, 10, 5)

if st.button("Generate Quiz"):
    if topic:
        with st.spinner("Generating quiz..."):
            quiz_questions = generate_quiz(topic, num_questions, st.session_state.api_key)
            if quiz_questions:
                st.session_state.quiz_questions = quiz_questions
                st.session_state.current_quiz_question = 0
                st.session_state.quiz_score = 0
                log_activity(st.session_state.username, "Generated Quiz", topic)
                st.rerun()
    else:
        st.warning("Please enter a topic.")

if 'quiz_questions' in st.session_state:
    q_index = st.session_state.current_quiz_question
    questions = st.session_state.quiz_questions

    if q_index < len(questions):
        question = questions[q_index]
        st.subheader(f"Question {q_index + 1}/{len(questions)}")
        st.write(question['question'])

        user_answer = st.radio("Choose your answer:", options=question['options'], index=None, key=f"q_{q_index}")

        if st.button("Submit Answer", key=f"submit_{q_index}"):
            if user_answer:
                if user_answer == question['correct_answer']:
                    st.success("Correct!")
                    st.session_state.quiz_score += 1
                else:
                    st.error("Incorrect.")

                st.info(f"**Explanation:** {question['explanation']}")
                st.session_state.current_quiz_question += 1
                time.sleep(3)
                st.rerun()
            else:
                st.warning("Please select an answer.")
    else:
        st.success(f"Quiz Complete! Score: {st.session_state.quiz_score}/{len(questions)}")
        log_activity(st.session_state.username, "Completed Quiz", f"Score: {st.session_state.quiz_score}/{len(questions)}")
        if st.button("Take Another Quiz"):
            del st.session_state.quiz_questions
            st.rerun()
