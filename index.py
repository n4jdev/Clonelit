from http.server import BaseHTTPRequestHandler
import json
import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def get_browser():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch()
    return playwright, browser

class Conversation:
    def __init__(self):
        self.conversation_id = None
        self.page = None
        self.playwright = None
        self.browser = None

    async def init_conversation(self):
        self.playwright, self.browser = await get_browser()
        context = await self.browser.new_context()
        self.page = await context.new_page()
        await self.page.goto("https://pi.ai/talk")
        await asyncio.sleep(5)  # Wait for the page to load

        try:
            response = await self.page.evaluate("""
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

            self.conversation_id = response['mainConversation']['sid']
        except Exception as e:
            print(f"Error in init_conversation: {str(e)}")
            raise

    async def ask(self, text):
        if not self.page:
            await self.init_conversation()

        try:
            response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch("https://pi.ai/api/chat", {{
                        method: "POST",
                        headers: {{
                            "Accept": "text/event-stream",
                            "Content-Type": "application/json",
                            "X-Api-Version": "3"
                        }},
                        body: JSON.stringify({{
                            conversation: "{self.conversation_id}",
                            text: "{text}"
                        }})
                    }});
                    return await response.text();
                }}
            """)

            return response
        except Exception as e:
            print(f"Error in ask: {str(e)}")
            return "An error occurred. Please try again."
        finally:
            await self.cleanup()

    async def cleanup(self):
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def stream_audio(text, voice_id):
    conversation = Conversation()
    await conversation.init_conversation()
    
    response = await conversation.ask(text)
    
    # Here you would typically process the response and generate audio
    # For this example, we'll simulate audio streaming with text chunks
    chunks = response.split()
    for chunk in chunks:
        # Simulate audio processing delay
        await asyncio.sleep(0.1)
        yield chunk.encode()

def parse_json_body(handler):
    content_length = int(handler.headers['Content-Length'])
    post_data = handler.rfile.read(content_length)
    return json.loads(post_data.decode('utf-8'))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write("Welcome to the TTS API!".encode())

    def do_POST(self):
        if self.path == '/api/tts':
            try:
                data = parse_json_body(self)
                if 'text' not in data or 'voice' not in data:
                    self.send_error(400, "Text and voice are required")
                    return

                text = data['text']
                voice = int(data['voice'])

                if not 1 <= voice <= 8:
                    self.send_error(400, "Voice must be between 1 and 8")
                    return

                if len(text) > 500:
                    self.send_error(400, "Text exceeds character limit")
                    return

                self.send_response(200)
                self.send_header('Content-type', 'audio/mpeg')
                self.send_header('Transfer-Encoding', 'chunked')
                self.end_headers()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                for chunk in loop.run_until_complete(stream_audio(text, voice)):
                    self.wfile.write(chunk)

            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")
