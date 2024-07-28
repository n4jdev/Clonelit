import os
import json
import asyncio
from flask import Flask, request, Response, stream_with_context
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

app = Flask(__name__)

MAX_TEXT_LENGTH = 500  # Maximum allowed text length

class TTSClient:
    def __init__(self):
        self.page = None

    async def init_browser(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        )
        self.page = await context.new_page()
        await self.page.goto("https://pi.ai/talk")
        await asyncio.sleep(5)  # Wait for the page to load

    async def generate_speech(self, text, voice_id):
        if not self.page:
            await self.init_browser()

        try:
            response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch("https://pi.ai/api/tts", {{
                        method: "POST",
                        headers: {{
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                            "X-Api-Version": "3"
                        }},
                        body: JSON.stringify({{
                            text: "{text}",
                            voice: {voice_id}
                        }})
                    }});
                    return await response.json();
                }}
            """)

            if 'url' in response:
                audio_response = await self.page.evaluate(f"""
                    async () => {{
                        const response = await fetch("{response['url']}");
                        const reader = response.body.getReader();
                        const chunks = [];
                        while (true) {{
                            const {{done, value}} = await reader.read();
                            if (done) break;
                            chunks.push(value);
                        }}
                        return chunks;
                    }}
                """)
                return audio_response
            else:
                raise Exception("Failed to generate speech")
        except Exception as e:
            print(f"Error in generate_speech: {str(e)}")
            raise

tts_client = TTSClient()

@app.route('/api/tts', methods=['POST'])
async def tts():
    data = request.json
    text = data.get('text', '')
    voice = data.get('voice', 1)

    if not text or len(text) > MAX_TEXT_LENGTH:
        return {'error': f'Text must be between 1 and {MAX_TEXT_LENGTH} characters'}, 400

    if not 1 <= voice <= 8:
        return {'error': 'Voice must be between 1 and 8'}, 400

    try:
        audio_chunks = await tts_client.generate_speech(text, voice)

        def generate():
            for chunk in audio_chunks:
                yield bytes(chunk)

        return Response(stream_with_context(generate()), mimetype='audio/mpeg')
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
