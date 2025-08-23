import streamlit as st
from gtts import gTTS
import io
from app import log_activity

st.set_page_config(page_title="AI Voice Narrator", layout="wide")

def generate_audio(text):
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"Failed to generate audio: {e}")
        return None

st.title("🔊 AI Voice Narrator")
st.info("Convert any text into a realistic voice narration.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in to use this feature.")
    st.stop()

text_to_narrate = st.text_area("Enter text to narrate:", height=250)

if st.button("Generate Audio"):
    if text_to_narrate:
        with st.spinner("Generating audio..."):
            audio_bytes = generate_audio(text_to_narrate)
            if audio_bytes:
                st.success("Audio generated!")
                st.audio(audio_bytes, format='audio/mp3')
                st.download_button("Download Audio (MP3)", audio_bytes, "narration.mp3", "audio/mp3")
                log_activity(st.session_state.username, "Generated Voice Narration")
    else:
        st.warning("Please enter text to narrate.")
