# clonelit_app.py

import streamlit as st
import asyncio
import os
import json
from tts_utils import upload_file_and_get_url, generate_tts

# Predefined voices
with open('predefined_voices.json', 'r') as f:
    PREDEFINED_VOICES = json.load(f)

# Sample text
SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog. This sentence contains every letter in the English alphabet."

def main():
    st.set_page_config(page_title="Clonelit - Advanced TTS App", layout="wide")

    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    st.title("🎙️ Clonelit - Advanced TTS App")
    st.markdown("Generate TTS of your favorite celebrities or clone your own voice!")

    col1, col2 = st.columns(2)

    with col1:
        st.header("🔊 Predefined Voices")
        selected_voice = st.selectbox("Choose a predefined voice:", list(PREDEFINED_VOICES.keys()))
        st.header("🎭 Clone Your Own Voice")
        uploaded_file = st.file_uploader("Upload a voice sample (MP3, M4A, WAV)", type=['mp3','m4a','wav'])

    with col2:
        st.markdown("---")
        
        st.header("⚙️ TTS Settings")
        speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.1)
        st.header("✍️ Enter Text")
        text_input = st.text_area("Enter text to convert to speech", value=SAMPLE_TEXT, height=150)
        
        if st.button("🚀 Generate TTS"):
            if not text_input:
                st.error("Please enter some text to convert to speech.")
                return

            if uploaded_file:
                with st.spinner("Processing voice sample..."):
                    with open("temp_voice_sample.mp3", "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    s3_url = asyncio.run(upload_file_and_get_url("temp_voice_sample.mp3", "https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice"))
                    
                    if s3_url:
                        st.success("Voice sample processed successfully")
                    else:
                        st.error("Failed to process voice sample")
                        return
                    
                    os.remove("temp_voice_sample.mp3")
            else:
                s3_url = PREDEFINED_VOICES[selected_voice]

            with st.spinner("Generating speech..."):
                audio_content = generate_tts(text_input, s3_url, speed=speed, temperature=temperature)
                
                if audio_content:
                    st.audio(audio_content, format="audio/mp3")
                    st.download_button(
                        label="Download Audio",
                        data=audio_content,
                        file_name="generated_speech.mp3",
                        mime="audio/mp3"
                    )
                else:
                    st.error("Failed to generate speech")

    st.markdown("---")
    st.markdown("### 📝 How to use Clonelit")
    st.markdown("""
    1. Choose a predefined voice or upload your own voice sample.
    2. Adjust the TTS settings if needed.
    3. Edit the text you want to convert to speech or use the provided sample text.
    4. Click 'Generate TTS' to create your audio.
    5. Play the generated audio or download it.
    """)

    st.markdown("---")
    st.caption("Note: This app uses external APIs for voice cloning and text-to-speech generation.")

if __name__ == "__main__":
    main()
