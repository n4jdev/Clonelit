from flask import Flask, request, Response, stream_with_context
from pi_ai_client import PiAIClient
import logging
import asyncio
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        try:
            conversation_id = loop.run_until_complete(pi_ai_client.init_conversation())
            chat_response = loop.run_until_complete(pi_ai_client.send_message(conversation_id, text))
            
            if not chat_response or 'received_sid' not in chat_response:
                logger.error("Failed to get a valid response from pi.ai")
                yield b''
                return

            audio_stream = loop.run_until_complete(pi_ai_client.get_voice(chat_response['received_sid'], voice))
            for chunk in audio_stream:
                yield chunk
        except Exception as e:
            logger.error(f"Error in text_to_speech: {str(e)}")
            yield b''
        finally:
            loop.close()

    return Response(stream_with_context(generate()), mimetype='audio/mp3')

# Vercel requires this
app = app
