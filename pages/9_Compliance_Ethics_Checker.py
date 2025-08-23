import streamlit as st
import openai
from PyPDF2 import PdfReader
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Compliance & Ethics Checker",
    page_icon="📌",
    layout="wide"
)

# --- Function to Query OpenAI API ---
def query_openai_api(system_prompt, user_prompt, api_key):
    """
    Sends a prompt to the OpenAI API and returns the response.
    """
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
        st.error(f"An error occurred with the OpenAI API request: {e}")
        return None

# --- Function to Extract Text from Uploaded File ---
def extract_text(uploaded_file):
    """
    Extracts text from an uploaded PDF or TXT file.
    """
    try:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            return "".join(page.extract_text() for page in reader.pages if page.extract_text())
        else: # Assumes text file
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        return None

# --- Streamlit User Interface ---
st.title("📌 AI Compliance & Ethics Checker")
st.info("Review your AI policy drafts against key ethical and regulatory principles.")

# Securely get OpenAI API Key
# For local development, you can create a .env file with your key
# For deployment (e.g., Streamlit Community Cloud), use st.secrets
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    api_key = st.text_input("Enter your OpenAI API Key", type="password", key="api_key_input")

if not api_key:
    st.warning("Please enter your OpenAI API Key to proceed.")
    st.stop()

# File Uploader
uploaded_file = st.file_uploader(
    "Upload your AI policy draft (PDF or TXT):", 
    type=["pdf", "txt"]
)

if uploaded_file:
    # Extract text from the uploaded document
    with st.spinner("Processing document..."):
        policy_text = extract_text(uploaded_file)
    
    if policy_text:
        st.success(f"Successfully processed '{uploaded_file.name}'.")
        
        # Display an expander with the document's text
        with st.expander("View extracted text"):
            st.text_area("", policy_text, height=200)

        # Button to trigger the review
        if st.button("Review Policy"):
            with st.spinner("Reviewing policy with AI Ethics Officer... This may take a moment."):
                system_prompt = "You are an expert AI Ethics Officer."
                user_prompt = f"""
                Please review the following company AI policy draft.
                
                Check it thoroughly against the principles of:
                - **Fairness:** Does the policy address potential biases in AI models and data?
                - **Transparency:** Does it explain how AI decisions are made and when AI is being used?
                - **GDPR Compliance:** Does it align with data protection, consent, and user rights under GDPR?
                - **EU AI Act Guidelines:** Does it consider risk classification and requirements for high-risk AI systems as outlined in the EU AI Act?

                Provide your analysis in the following structured format:
                
                ### 1. Strengths of this Policy
                * (List the positive aspects and well-addressed points here)
                
                ### 2. Weaknesses & Potential Risks
                * (List the gaps, ambiguities, or areas that pose a compliance or ethical risk)
                
                ### 3. Actionable Recommendations
                * (Provide clear, specific suggestions to improve the policy and mitigate risks)
                
                Use clear and concise business language suitable for an executive audience.
                
                ---
                **POLICY DRAFT:**
                {policy_text}
                ---
                """
                
                # Get the response from OpenAI
                response = query_openai_api(system_prompt, user_prompt, api_key)
                
                if response:
                    st.markdown("---")
                    st.subheader("AI Ethics Officer Review")
                    st.markdown(response)

