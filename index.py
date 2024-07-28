from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    data = request.json
    if not data or 'text' not in data or 'voice' not in data:
        return jsonify({"error": "Text and voice are required"}), 400
    
    text = data['text']
    voice = int(data['voice'])
    
    if not 1 <= voice <= 8:
        return jsonify({"error": "Voice must be between 1 and 8"}), 400
    
    if len(text) > 500:  # Example character limit
        return jsonify({"error": "Text exceeds character limit"}), 400

    # Here you would implement your TTS logic
    # For now, we'll just return a placeholder response
    return jsonify({"message": f"TTS request received. Text: {text}, Voice: {voice}"})

@app.route('/')
def home():
    return "Welcome to the TTS API!"

def handler(event, context):
    return app(event, context)
