from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from the TTS API!'
    }
