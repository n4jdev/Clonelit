import http.client
import json
import time
import io
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

HOST = 'pi.ai'
CONVERSATIONS_PATH = '/api/conversations'
CHAT_PATH = '/api/chat'
VOICE_PATH = '/api/chat/voice'

class PyChatAPI:
    def __init__(self):
        self.conversation_id = self.get_conversation_id()

    def make_request(self, method, path, headers, body=None):
        conn = http.client.HTTPSConnection(HOST)
        conn.request(method, path, body, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        return response, data

    def get_conversation_id(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'authority': 'pi.ai',
            'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
            'origin': 'https://pi.ai',
            'referer': 'https://pi.ai/talk',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'Cookie': '__Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=28MnnefdTV23iLTtJaYJdxU6magLYb4zpDGyMKHrHvw-1721964119-1.0.1.1-upkx6n8USULq_B4mAxmjY2Y1fh40DkcftOZXoRwQTHh0Th4MtCGN0Jin02G7ALcqrnx3huEnpGbujKoW9ETsBw'
        }
        response, data = self.make_request('POST', CONVERSATIONS_PATH, headers)
        try:
            data = json.loads(data)
            return data.get('sid')
        except json.JSONDecodeError:
            print(f"Error decoding JSON: {data}")
            return None

    def send_message(self, message):
        chat_data = json.dumps({"text": message, "conversation": self.conversation_id})
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/event-stream',
            'Content-Type': 'application/json',
            'authority': 'pi.ai',
            'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
            'origin': 'https://pi.ai',
            'referer': 'https://pi.ai/talk',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'x-api-version': '3',
            'Cookie': '__Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
        }
        response, data = self.make_request('POST', CHAT_PATH, headers, chat_data)

        received_sid = None
        full_response = ""
        for line in data.decode('utf-8').splitlines():
            if line.startswith('event: received'):
                received_data = json.loads(next(line for line in data.decode('utf-8').splitlines() if line.startswith('data:')).split('data: ')[1])
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
            'authority': 'pi.ai',
            'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
            'range': 'bytes=0-',
            'referer': 'https://pi.ai/talk',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'audio',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-origin',
            'Cookie': '__Host-session=r98ovC1suEw22c6xmspsp; __cf_bm=BS95IS_QPeqiUILdVHjCIV6YCd9Fs31a5egMZN8X0U0-1721961318-1.0.1.1-aPtKE.13enODokRbrdjpE7f31q68G0reBI2vmzK6rpmlFZfpAVQ_nIJYUPme_VOhC0TYuz5zAm4M34l.Xz1XFQ'
        }
        response, voice_data = self.make_request('GET', f'{VOICE_PATH}?mode=eager&voice=voice{voice_id}&messageSid={message_sid}', headers)
        return voice_data

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
