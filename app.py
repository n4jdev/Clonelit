import streamlit as st
import asyncio
import os
import json
import requests
from playwright.async_api import async_playwright

# Install Playwright browsers
os.system("playwright install")

def find_s3_url(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and value.startswith("s3://voice-cloning-zero-shot/"):
                return value
            result = find_s3_url(value)
            if result:
                return result
    elif isinstance(data, list):
        for item in data:
            result = find_s3_url(item)
            if result:
                return result
    return None

async def upload_file_and_get_url(file_path, page_url, timeout=60000):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        )
        page = await context.new_page()

        try:
            await page.goto(page_url, wait_until='domcontentloaded')
            file_input = await page.wait_for_selector('input[type="file"]', state='visible', timeout=10000)
            if not file_input:
                raise Exception("File input not found")

            await file_input.set_input_files(file_path)
            await page.wait_for_timeout(2000)

            async with page.expect_response(lambda response: "/workflow/start" in response.url, timeout=timeout) as response_info:
                response = await response_info.value

            if response.ok:
                api_response = await response.json()
                s3_url = find_s3_url(api_response)
                if s3_url:
                    return s3_url
                else:
                    st.error("Failed to find s3 URL in the response.")
                    return None
            else:
                st.error(f"API request failed with status {response.status}")
                return None

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

        finally:
            await browser.close()

def generate_tts(text, voice, output_format="mp3", speed=1, sample_rate=44100, temperature=0.4):
    url = "https://chirpy.play.ht/api/v2/tts/stream"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "authority": "chirpy.play.ht",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "origin": "https://play.ht",
        "referer": "https://play.ht/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "x-user-id": "86OEPNzxxsestqtf9k41quQAS8F3",
        "Authorization": "Bearer 418f05355cdc49d4b2f4f8fe31528e3e"
    }
    payload = {
        "text": text,
        "voice": voice,
        "output_format": output_format,
        "speed": speed,
        "sample_rate": sample_rate,
        "temperature": temperature,
        "voice_engine": "PlayHT2.0-gargamel",
        "voice_guidance": None,
        "text_guidance": 0.8
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"TTS API request failed with status {response.status_code}")
        return None

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
