import json
import time
import io
from flask import Flask, request, jsonify, send_file
import requests

app = Flask(__name__)

BASE_URL = 'https://pi.ai/api'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

class PyChatAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://pi.ai/talk',
            'Origin': 'https://pi.ai',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-Ua': '"Google Chrome";v="91", "Chromium";v="91", ";Not A Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
        self.conversation_id = self.get_conversation_id()

    def get_conversation_id(self):
        response = self.session.post(f'{BASE_URL}/conversations', json={})
        return response.json().get('sid')

    def send_message(self, message):
        chat_data = {"text": message, "conversation": self.conversation_id}
        response = self.session.post(f'{BASE_URL}/chat', json=chat_data, stream=True)
        
        received_sid = None
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('event: received'):
                    received_data = json.loads(next(response.iter_lines()).decode('utf-8').split('data: ')[1])
                    received_sid = received_data.get('sid')
                elif decoded_line.startswith('data:'):
                    try:
                        event_data = json.loads(decoded_line.split('data: ')[1])
                        if 'text' in event_data:
                            full_response += event_data['text']
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON: {decoded_line}")

        return full_response.strip(), received_sid

    def get_voice(self, message_sid, voice_id):
        voice_url = f'{BASE_URL}/chat/voice?mode=eager&voice=voice{voice_id}&messageSid={message_sid}'
        response = self.session.get(voice_url)
        return response.content

chat_api = PyChatAPI()

@app.route('/api/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get('text')
    voice = data.get('voice')

    if not text or not voice:
        return jsonify({"error": "Missing 'text' or 'voice' in request"}), 400

    if not 1 <= int(voice) <= 8:
        return jsonify({"error": "Voice must be between 1 and 8"}), 400

    try:
        response, received_sid = chat_api.send_message(text)
        
        if not received_sid:
            return jsonify({"error": "Failed to get message SID"}), 500

        voice_data = chat_api.get_voice(received_sid, voice)
        
        timestamp = int(time.time())
        filename = f"tts_output_{timestamp}.mp3"
        
        return send_file(
            io.BytesIO(voice_data),
            mimetype='audio/mp3',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
