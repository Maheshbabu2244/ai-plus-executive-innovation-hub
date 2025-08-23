import streamlit as st
from gtts import gTTS
import openai
import re
import io
import base64
import json
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image
from app import log_activity

st.set_page_config(page_title="Text-to-Video Generator", layout="wide")

def query_openai_text_api(system_prompt, user_prompt, api_key):
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
        st.error(f"OpenAI Text API Error: {e}")
    return None

def generate_image_with_openai(prompt, api_key):
    openai.api_key = api_key
    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json"
        )
        return response.data[0].b64_json
    except Exception as e:
        st.error(f"OpenAI Image Generation Error: {e}")
    return None

def generate_storyboard(script, api_key):
    system_prompt = "You are a creative video director."
    user_prompt = f"""
    Based on the following script, create a storyboard with 4-6 scenes.
    For each scene, provide a 'visual_description' for an AI image generator (detailed, cinematic, vivid) and a 'narration' script.
    Return as a valid JSON list of dictionaries. Example:
    [
      {{"scene": 1, "visual_description": "A panoramic view of a modern city skyline at sunrise...", "narration": "In a world of constant change..."}}
    ]
    SCRIPT: --- {script} ---
    """
    response_text = query_openai_text_api(system_prompt, user_prompt, api_key)
    if response_text:
        try:
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            return json.loads(json_match.group(0))
        except (AttributeError, json.JSONDecodeError):
            st.error("Failed to parse storyboard.")
    return None

def create_video_from_storyboard(storyboard, api_key):
    clips = []
    full_narration = " ".join([scene.get('narration', '') for scene in storyboard])

    with st.spinner("Generating full audio narration..."):
        tts = gTTS(text=full_narration, lang='en')
        audio_filename = "full_narration.mp3"
        tts.save(audio_filename)
        main_audio = AudioFileClip(audio_filename)
        total_duration = main_audio.duration

    duration_per_scene = total_duration / len(storyboard)

    image_files = []
    for i, scene in enumerate(storyboard):
        status_placeholder = st.empty()
        status_placeholder.info(f"🎨 Generating image for scene {i+1}/{len(storyboard)}...")
        b64_json = generate_image_with_openai(scene['visual_description'], api_key)
        if b64_json:
            img_bytes = base64.b64decode(b64_json)
            img = Image.open(io.BytesIO(img_bytes))
            img_path = f"scene_{i+1}.png"
            img.save(img_path)
            image_files.append(img_path)
            status_placeholder.empty()
        else:
            st.error(f"Could not generate image for scene {i+1}. Skipping.")
            continue

    with st.spinner("🎬 Compiling video... this may take a moment."):
        for img_path in image_files:
            clip = ImageClip(img_path).set_duration(duration_per_scene)
            clip = clip.resize(lambda t: 1 + 0.05 * t).set_pos(('center', 'center'))
            clips.append(clip)

        if not clips:
            st.error("No video clips were created. Aborting.")
            return None

        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(main_audio)

        video_filename = "generated_video.mp4"
        video.write_videofile(video_filename, fps=24, codec='libx264', audio_codec='aac')

    return video_filename

st.title("📝 Text-to-Video Generator")
st.info("This tool generates a real video file from your script using AI image generation and voice narration.")

if 'username' not in st.session_state or not st.session_state.username:
    st.warning("Please log in to use this feature.")
    st.stop()
if not st.session_state.get('api_key'):
    st.error("Please add your OpenAI API Key to the app's secrets.")
    st.stop()

script = st.text_area("Enter your video script here:", height=200)

if st.button("Generate Video"):
    if script:
        storyboard = generate_storyboard(script, st.session_state.api_key)
        if storyboard:
            video_file = create_video_from_storyboard(storyboard, st.session_state.api_key)
            if video_file:
                st.success("Video generated successfully!")
                log_activity(st.session_state.username, "Generated Video")

                video_bytes = open(video_file, 'rb').read()
                st.video(video_bytes)
                st.download_button("Download Video (MP4)", video_bytes, "ai_generated_video.mp4", "video/mp4")
    else:
        st.warning("Please enter a script.")
