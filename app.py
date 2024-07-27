import asyncio
from flask import Flask, request, Response, stream_with_context
from pi_ai_client import PiAIClient
import logging
import os
import subprocess

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Install Playwright and download browser on first run
if not os.path.exists("/tmp/.playwright-installed"):
    logger.info("Installing Playwright and downloading browser...")
    subprocess.run(["pip", "install", "playwright"])
    subprocess.run(["playwright", "install", "chromium"])
    open("/tmp/.playwright-installed", "w").close()

pi_ai_client = PiAIClient()

@app.route('/api/tts', methods=['GET'])
def text_to_speech():
    text = request.args.get('text')
    voice = request.args.get('voice', default='1')

    if not text:
        return 'Missing text parameter', 400

    try:
        voice = int(voice)
        if voice < 1 or voice > 8:
            return 'Invalid voice parameter. Must be between 1 and 8.', 400
    except ValueError:
        return 'Invalid voice parameter. Must be an integer.', 400

    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        conversation_id = loop.run_until_complete(pi_ai_client.init_conversation())
        
        chat_response = loop.run_until_complete(pi_ai_client.send_message(conversation_id, text))
        if not chat_response or 'received_sid' not in chat_response:
            logger.error("Failed to get a valid response from pi.ai")
            yield b''
            return

        audio_stream = loop.run_until_complete(pi_ai_client.get_voice(chat_response['received_sid'], voice))
        for chunk in audio_stream:
            yield chunk

    return Response(stream_with_context(generate()), mimetype='audio/mp3')

# Add this line for Vercel
app = app
