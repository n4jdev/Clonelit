# clonelit_app.py

import streamlit as st
import asyncio
import os
from tts_utils import upload_file_and_get_url, generate_tts

# Predefined voices
PREDEFINED_VOICES = {
    "Morgan Freeman": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/voices/morgan_freeman/manifest.json",
    "Barack Obama": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/voices/barack_obama/manifest.json",
    "Emma Watson": "s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/voices/emma_watson/manifest.json",
}

def main():
    st.set_page_config(page_title="Clonelit - Advanced TTS App", layout="wide")

    st.title("🎙️ Clonelit - Advanced TTS App")
    st.markdown("Generate TTS of your favorite celebrities or clone your own voice!")

    col1, col2 = st.columns(2)

    with col1:
        st.header("🔊 Predefined Voices")
        selected_voice = st.selectbox("Choose a predefined voice:", list(PREDEFINED_VOICES.keys()))
        
        st.markdown("---")
        
        st.header("🎭 Clone Your Own Voice")
        uploaded_file = st.file_uploader("Upload a voice sample (MP3, M4A, WAV)", type=['mp3','m4a','wav'])

    with col2:
        st.header("✍️ Enter Text")
        text_input = st.text_area("Enter text to convert to speech", height=150)
        
        st.markdown("---")
        
        st.header("⚙️ TTS Settings")
        speed = st.slider("Speed", 0.5, 2.0, 1.0, 0.1)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.1)

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
    2. Enter the text you want to convert to speech.
    3. Adjust the TTS settings if needed.
    4. Click 'Generate TTS' to create your audio.
    5. Play the generated audio or download it.
    """)

    st.markdown("---")
    st.caption("Note: This app uses external APIs for voice cloning and text-to-speech generation.")

if __name__ == "__main__":
    main()
