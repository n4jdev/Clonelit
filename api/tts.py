import json
import base64
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
from playwright.async_api import async_playwright

MAX_CHAR_LIMIT = 500

def handler(event, context):
    return TTSHandler(event, context)

class TTSHandler(BaseHTTPRequestHandler):
    def __init__(self, event, context):
        self.event = event
        self.context = context

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

    def handle_request(self):
        if self.event['httpMethod'] == 'GET' and self.event['path'].startswith('/api/tts'):
            params = parse_qs(self.event['queryStringParameters']) if self.event['queryStringParameters'] else {}
            voice = params.get('voice', ['1'])[0]
            text = params.get('text', [''])[0]

            if not text:
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": "Missing 'text' parameter"})
                }

            if len(text) > MAX_CHAR_LIMIT:
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": f"Text exceeds {MAX_CHAR_LIMIT} character limit"})
                }

            if voice not in map(str, range(1, 9)):
                return {
                    'statusCode': 400,
                    'body': json.dumps({"error": "Invalid 'voice' parameter. Must be between 1 and 8."})
                }

            async def stream_wrapper():
                audio_data = b""
                async for chunk in self.generate_audio(text, voice):
                    audio_data += chunk
                return base64.b64encode(audio_data).decode('utf-8')

            audio_base64 = asyncio.get_event_loop().run_until_complete(stream_wrapper())

            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'audio/mpeg',
                    'Content-Transfer-Encoding': 'base64'
                },
                'body': audio_base64,
                'isBase64Encoded': True
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({"error": "Not Found"})
            }

    def __call__(self, event, context):
        return self.handle_request()
