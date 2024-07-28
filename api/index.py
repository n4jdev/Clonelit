from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/tts', methods=['POST'])
def tts_endpoint():
    return jsonify({"message": "TTS endpoint reached"})

@app.route('/')
def home():
    return "Hello from Flask!"

if __name__ == '__main__':
    app.run(debug=True)
