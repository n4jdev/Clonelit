import json
import base64
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from playwright.async_api import async_playwright

MAX_CHAR_LIMIT = 500

class TTSHandler(BaseHTTPRequestHandler):
    async def generate_audio(self, text, voice_id):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                device_scale_factor=1,
            )
            page = await context.new_page()
            await page.goto("https://pi.ai/talk")
            await asyncio.sleep(5)  # Wait for the page to load

            try:
                response = await page.evaluate("""
                    async () => {
                        const response = await fetch("https://pi.ai/api/chat/start", {
                            method: "POST",
                            headers: {
                                "accept": "application/json",
                                "X-Api-Version": "3",
                                "content-type": "application/json"
                            },
                            body: "{}"
                        });
                        return await response.json();
                    }
                """)

                if not isinstance(response, dict) or 'mainConversation' not in response:
                    raise Exception("Failed to init conversation")

                conversation_id = response['mainConversation']['sid']

                audio_response = await page.evaluate(f"""
                    async () => {{
                        const response = await fetch("https://pi.ai/api/chat", {{
                            method: "POST",
                            headers: {{
                                "Accept": "text/event-stream",
                                "Content-Type": "application/json",
                                "X-Api-Version": "3"
                            }},
                            body: JSON.stringify({{
                                conversation: "{conversation_id}",
                                text: "{text}"
                            }})
                        }});
                        return await response.text();
                    }}
                """)

                audio_data = b""
                for line in audio_response.split('\n'):
                    if line.startswith('data: '):
                        try:
                            data = json.loads(line[6:])
                            if isinstance(data, dict) and 'audio' in data:
                                audio_chunk = base64.b64decode(data['audio'])
                                audio_data += audio_chunk
                                yield audio_chunk
                        except json.JSONDecodeError:
                            pass

            except Exception as e:
                print(f"Error in generate_audio: {str(e)}")
                yield b""
            finally:
                await browser.close()

    def do_GET(self):
        if self.path.startswith('/api/tts'):
            params = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            voice = params.get('voice', ['1'])[0]
            text = params.get('text', [''])[0]

            if not text:
                self.send_error(400, "Missing 'text' parameter")
                return

            if len(text) > MAX_CHAR_LIMIT:
                self.send_error(400, f"Text exceeds {MAX_CHAR_LIMIT} character limit")
                return

            if voice not in map(str, range(1, 9)):
                self.send_error(400, "Invalid 'voice' parameter. Must be between 1 and 8.")
                return

            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()

            async def stream_wrapper():
                async for chunk in self.generate_audio(text, voice):
                    self.wfile.write(chunk)
                    self.wfile.flush()

            asyncio.run(stream_wrapper())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        self.send_error(405, "Method Not Allowed")

def handler(event, context):
    return TTSHandler(event, context)
