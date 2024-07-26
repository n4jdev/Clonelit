import os
import json
import requests
from flask import Flask, request, jsonify, send_file
import asyncio
import io

app = Flask(__name__)

CONVERSATIONS_URL = 'https://pi.ai/api/conversations'
CHAT_URL = 'https://pi.ai/api/chat'
VOICE_URL = 'https://pi.ai/api/chat/voice'

HEADERS = {
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
    'x-api-version': '3',
}

COOKIES = {
    '__Host-session': 'r98ovC1suEw22c6xmspsp',
    '__cf_bm': '28MnnefdTV23iLTtJaYJdxU6magLYb4zpDGyMKHrHvw-1721964119-1.0.1.1-upkx6n8USULq_B4mAxmjY2Y1fh40DkcftOZXoRwQTHh0Th4MtCGN0Jin02G7ALcqrnx3huEnpGbujKoW9ETsBw',
}

async def get_conversation_id():
    response = requests.post(CONVERSATIONS_URL, headers=HEADERS, cookies=COOKIES, json={})
    data = response.json()
    return data.get('sid')

async def send_message(conversation_id, message):
    chat_data = json.dumps({"text": message, "conversation": conversation_id})
    response = requests.post(CHAT_URL, headers=HEADERS, cookies=COOKIES, data=chat_data)
    
    received_sid = None
    full_response = ""
    
    for line in response.text.splitlines():
        if line.startswith('event: received'):
            received_data = json.loads(next(line for line in response.text.splitlines() if line.startswith('data:')).split('data: ')[1])
            received_sid = received_data.get('sid')
        elif line.startswith('data:'):
            try:
                event_data = json.loads(line[5:])
                if 'text' in event_data:
                    full_response += event_data['text']
            except json.JSONDecodeError:
                pass

    return full_response.strip(), received_sid

async def get_voice(message_sid, voice_id):
    voice_url = f"{VOICE_URL}?mode=eager&voice=voice{voice_id}&messageSid={message_sid}"
    response = requests.get(voice_url, headers=HEADERS, cookies=COOKIES)
    return response.content

@app.route('/api/tts', methods=['POST'])
async def tts():
    data = request.json
    text = data.get('text')
    voice = data.get('voice')

    if not text or not voice:
        return jsonify({"error": "Missing 'text' or 'voice' in request"}), 400

    if not 1 <= int(voice) <= 8:
        return jsonify({"error": "Voice must be between 1 and 8"}), 400

    try:
        conversation_id = await get_conversation_id()
        response, received_sid = await send_message(conversation_id, text)
        
        if not received_sid:
            return jsonify({"error": "Failed to get message SID"}), 500

        voice_data = await get_voice(received_sid, voice)
        
        return send_file(
            io.BytesIO(voice_data),
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='tts_output.mp3'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
