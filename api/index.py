import subprocess
import json
import time
import io
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

CONVERSATIONS_CURL = '''
curl -X POST 'https://pi.ai/api/conversations' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'origin: https://pi.ai' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: empty' -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-origin' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=28MnnefdTV23iLTtJaYJdxU6magLYb4zpDGyMKHrHvw-1721964119-1.0.1.1-upkx6n8USULq_B4mAxmjY2Y1fh40DkcftOZXoRwQTHh0Th4MtCGN0Jin02G7ALcqrnx3huEnpGbujKoW9ETsBw' -d '{}'
'''

CHAT_CURL = '''
curl -X POST 'https://pi.ai/api/chat' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'Accept: text/event-stream' -H 'Content-Type: application/json' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'origin: https://pi.ai' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: empty' -H 'sec-fetch-mode: cors' -H 'sec-fetch-site: same-origin' -H 'x-api-version: 3' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ' -d '{}'
'''

VOICE_CURL = '''
curl -X GET 'https://pi.ai/api/chat/voice?mode=eager&voice=voice{}&messageSid={}' -H 'User-Agent: Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36' -H 'authority: pi.ai' -H 'accept-language: en-PH,en-US;q=0.9,en;q=0.8' -H 'range: bytes=0-' -H 'referer: https://pi.ai/talk' -H 'sec-ch-ua: "Not-A.Brand";v="99", "Chromium";v="124"' -H 'sec-ch-ua-mobile: ?1' -H 'sec-ch-ua-platform: "Android"' -H 'sec-fetch-dest: audio' -H 'sec-fetch-mode: no-cors' -H 'sec-fetch-site: same-origin' -H 'Cookie: __Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
'''

class PyChatAPI:
    def __init__(self):
        self.conversation_id = self.get_conversation_id()

    def run_curl(self, curl_command):
        try:
            result = subprocess.run(curl_command, shell=True, check=True, capture_output=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running curl command: {e}")
            print(f"Stderr: {e.stderr}")
            return None

    def get_conversation_id(self):
        response = self.run_curl(CONVERSATIONS_CURL)
        try:
            data = json.loads(response)
            return data.get('sid')
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {response}")
            return None

    def send_message(self, message):
        chat_data = json.dumps({"text": message, "conversation": self.conversation_id})
        chat_curl = CHAT_CURL.replace("'{}'", f"'{chat_data}'")
        response = self.run_curl(chat_curl)

        received_sid = None
        full_response = ""
        for line in response.decode('utf-8').splitlines():
            if line.startswith('event: received'):
                received_data = json.loads(next(line for line in response.decode('utf-8').splitlines() if line.startswith('data:')).split('data: ')[1])
                received_sid = received_data.get('sid')
            elif line.startswith('data:'):
                try:
                    event_data = json.loads(line[5:])
                    if 'text' in event_data:
                        full_response += event_data['text']
                except json.JSONDecodeError:
                    print(f"Error decoding JSON: {line}")

        return full_response.strip(), received_sid

    def get_voice(self, message_sid, voice_id):
        voice_curl = VOICE_CURL.format(voice_id, message_sid)
        voice_response = self.run_curl(voice_curl)
        return voice_response

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
