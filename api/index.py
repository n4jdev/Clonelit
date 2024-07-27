from flask import Flask, request, Response, stream_with_context
from tts_service import TTSService
import asyncio

app = Flask(__name__)
tts_service = TTSService()

def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coroutine)

@app.route('/api/tts', methods=['GET'])
def tts():
    voice = request.args.get('voice', default='1', type=str)
    text = request.args.get('text', default='', type=str)

    if not text:
        return "Text parameter is required", 400

    if voice not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        return "Invalid voice parameter. Choose from 1-8", 400

    def generate():
        for chunk in run_async(tts_service.generate_speech(text, voice)):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='audio/mpeg')

# Vercel requires a handler function
def handler(request):
    return app(request.environ, lambda x, y: y)
