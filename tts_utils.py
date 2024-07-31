# tts_utils.py

import os
import requests
from playwright.async_api import async_playwright
import streamlit as st

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

def generate_tts(text, voice, output_format="mp3", speed=1, quality="premium"):
    url = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "authority": "europe-west3-bubble-io-284016.cloudfunctions.net",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "origin": "https://playhttexttospeechdemo.bubbleapps.io",
        "referer": "https://playhttexttospeechdemo.bubbleapps.io/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "Authorization": "Bearer 8ccbf7cf6fdbfdaf509b29ac185d131d5928afa33b7ea216439ca60f8fc8d167fe7ac23843d74651bbabe15758bb01b0402369c8639ee3ffc1abe6adcd404b04bb70199773bbe672fe2567a05aadf7d7257b5ee00a05241057d7e08fbedbc8b59add5c15324cd7dc051f09d4e47fb1bfe255f8289adc0c078e0b454bf57d654f9736cab983340213519c694278f16239f06433c3b3500e7b0e7a663edd3c2b9e5bea159fa22ce6c3e2eba54e9c7d050f09706a72beaa9d88baafaa834a74f27823bc5306df0d3de38763480bc11252c2b11b6fa4d1f28e26aa3a1867072f21f5f3725b16482a236bc366b3bc4f1a406e740b8fb607e7326d88db61989de15753f4527f1d0443a81674423682e80b0f472f049a1de3d1169fc441cb1bc3a31909e14479c96c3eae448ad61af2"
    }
    payload = {
        "input": text,
        "voice": voice,
        "format": output_format,
        "mimeCode": "audio/mpeg",
        "speed": speed,
        "quality": quality
    }

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"TTS API request failed with status {response.status_code}")
        return None

# Install Playwright browsers
os.system("playwright install")
