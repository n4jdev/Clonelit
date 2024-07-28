import os
import asyncio
import base64
from flask import Flask, request, jsonify, Response, stream_with_context
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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

@app.route('/api/tts', methods=['POST'])
async def tts_endpoint():
    data = request.json
    if not data or 'text' not in data or 'voice' not in data:
        return jsonify({"error": "Text and voice are required"}), 400
    
    text = data['text']
    voice = int(data['voice'])
    
    if not 1 <= voice <= 8:
        return jsonify({"error": "Voice must be between 1 and 8"}), 400
    
    if len(text) > 500:  # Example character limit
        return jsonify({"error": "Text exceeds character limit"}), 400

    return Response(stream_with_context(stream_audio(text, voice)), content_type='audio/mpeg')

@app.route('/')
def home():
    return "Welcome to the TTS API!"

if __name__ == '__main__':
    app.run(debug=True)

# Vercel serverless function entry point
def handler(request):
    return app(request)
