from flask import Flask, request, Response, stream_with_context
from tts_service import TTSService
import asyncio

app = Flask(__name__)
tts_service = TTSService()

@app.route('/api/tts', methods=['GET'])
def tts():
    voice = request.args.get('voice', default='1', type=str)
    text = request.args.get('text', default='', type=str)

    if not text:
        return "Text parameter is required", 400

    if voice not in ['1', '2', '3', '4', '5', '6', '7', '8']:
        return "Invalid voice parameter. Choose from 1-8", 400

    def generate():
        for chunk in asyncio.run(tts_service.generate_speech(text, voice)):
            yield chunk

    return Response(stream_with_context(generate()), mimetype='audio/mpeg')

# Vercel requires a handler function
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
