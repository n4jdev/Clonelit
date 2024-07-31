# tts_utils.py

import os
import requests
from playwright.async_api import async_playwright
import streamlit as st
from itertools import cycle

# List of authorization tokens and user IDs
AUTH_DATA = [
    {"token": "Bearer e4c99eb7dc6942bd85d5055f05bcb56b", "user_id": "cOkx04WHR1VmPJRCJBvBSa59kDz2"},
    {"token": "Bearer 0cbc3b554cc144bb897952eea31dfed9", "user_id": "k22sReMUoMNZ6c6wZiqq3GNHILK2"},
    {"token": "Bearer fc638819fc414197852cb8bbc57c53f8", "user_id": "SET8dBW3qjYeu9cUO9vM2WaIAt63"},
    {"token": "Bearer 5044a7541ff546cc9d893c31a5593484", "user_id": "UyssnOM498O343FGgYjhfHQbol63"},  # Fixed this line
    {"token": "Bearer 72a5e9bd3a624ca5ba674e91ef775bbb", "user_id": "7zywrY6k1w6dAZdusprVbBj9AAn32"},
    {"token": "Bearer e4a2c21fe543434a8b8bf2841f0ca625", "user_id": "2VUvgzQrtIMJqqMuMbfUlByfQt32"},
    {"token": "Bearer 86b64bac5b8e4b6389ff21b38d012f88", "user_id": "tbUPoYCw2AaZDrNmFyc1lAAC65r2"},
    {"token": "Bearer 0dfdf9b39b8941a6a0f76ceadd66627a", "user_id": "nTEPbMgjSZZmr63H5HoEEC3Snc73"}  # Fixed this line
]

# Create a cycler for the auth data
auth_data_cycler = cycle(AUTH_DATA)

def get_next_auth_data():
    return next(auth_data_cycler)

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
    auth_data = get_next_auth_data()
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
        "x-user-id": auth_data["user_id"],
        "Authorization": auth_data["token"]
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

# Install Playwright browsers
os.system("playwright install")
