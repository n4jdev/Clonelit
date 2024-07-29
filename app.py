import streamlit as st
import requests
import json
import base64
import os
import logging
import io

# Set up logging
class StreamlitHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []

    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
streamlit_handler = StreamlitHandler()
logger.addHandler(streamlit_handler)

def get_upload_url(file_name, file_size):
    logger.info(f"Getting upload URL for file: {file_name}, size: {file_size}")
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/fileupload/geturl"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
        'authority': 'playhttexttospeechdemo.bubbleapps.io',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-bubble-breaking-revision': '5',
        'x-bubble-fiber-id': '1722237865117x100995695629340080',
        'x-bubble-pl': '1722237591965x1002',
        'x-bubble-r': 'https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        "public": True,
        "service": "bubble",
        "timezone_string": "Asia/Manila",
        "serialized_context": {
            "client_state": {
                "element_instances": {
                    "cmMuK": {"dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMuK", "parent_element_id": "cmMsT"},
                    "cmMxX": {"dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMxX", "parent_element_id": "cmMuK"}
                },
                "element_state": {"1348695171700984260__LOOKUP__ElementInstance::cmMuK": {"group_data": None}},
                "other_data": {"Current Page Scroll Position": 0, "Current Page Width": 360},
                "cache": {},
                "exists": {}
            },
            "element_id": "cmMxX",
            "current_date_time": 1722237864807,
            "timezone_offset": -480,
            "timezone_string": "Asia/Manila",
            "inputs_must_be_valid": False,
            "current_wf_params": {}
        },
        "name": file_name,
        "size": file_size,
        "content_type": "audio/mpeg"
    }
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"Upload URL response: {response.text}")
    return response.json()

def upload_file(upload_url, fields, file_path):
    logger.info(f"Uploading file: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}
        response = requests.post(upload_url, data=fields, files=files)
    logger.info(f"Upload response status code: {response.status_code}")
    return response.status_code == 204

def start_workflow(file_url):
    logger.info(f"Starting workflow with file URL: {file_url}")
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/workflow/start"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
        'authority': 'playhttexttospeechdemo.bubbleapps.io',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'x-bubble-breaking-revision': '5',
        'x-bubble-fiber-id': '1722257465861x527160234769953800',
        'x-bubble-pl': '1722257441166x3245',
        'x-bubble-r': 'https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice',
        'x-requested-with': 'XMLHttpRequest',
    }
    data = {
        "wait_for": [],
        "app_last_change": "19875058729",
        "client_breaking_revision": 5,
        "calls": [{
            "client_state": {
                "element_instances": {
                    "cmMxX": {"dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMxX", "parent_element_id": "cmMuK"},
                    "cmMsq": {"dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMsq", "parent_element_id": "cmMsk"},
                    "cmMuK": {"dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMuK", "parent_element_id": "cmMsT"}
                },
                "element_state": {
                    "1348695171700984260__LOOKUP__ElementInstance::cmMxX": {
                        "is_visible": True,
                        "value_that_is_valid": file_url,
                        "value": file_url
                    },
                    "1348695171700984260__LOOKUP__ElementInstance::cmMuK": {"group_data": None}
                },
                "other_data": {"Current Page Scroll Position": 0, "Current Page Width": 360},
                "cache": {},
                "exists": {}
            },
            "run_id": "1722257465855x763661702156541800",
            "server_call_id": "1722257465861x213023273471344440",
            "item_id": "cmMxd",
            "element_id": "cmMxX",
            "uid_generator": {"timestamp": 1722257465855, "seed": 27772894338195630},
            "random_seed": 0.20947760161398143,
            "current_date_time": 1722237867610,
            "current_wf_params": {}
        }],
        "timezone_offset": -480,
        "timezone_string": "Asia/Manila",
        "user_id": "1722234365445x688391142658434600"
    }
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"Workflow response: {response.text}")
    return response.json()

def generate_tts(voice_id, text):
    logger.info(f"Generating TTS with voice ID: {voice_id}, text: {text}")
    url = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
        'Content-Type': 'application/json',
        'authority': 'europe-west3-bubble-io-284016.cloudfunctions.net',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer 8ccbf7cf6fdbfdaf509b29ac185d131d5928afa33b7ea216439ca60f8fc8d167fe7ac23843d74651bbabe15758bb01b0402369c8639ee3ffc1abe6adcd404b04bb70199773bbe672fe2567a05aadf7d7257b5ee00a05241057d7e08fbedbc8b59add5c15324cd7dc051f09d4e47fb1bfe255f8289adc0c078e0b454bf57d654f9736cab983340213519c694278f16239f06433c3b3500e7b0e7a663edd3c2b9e5bea159fa22ce6c3e2eba54e9c7d050f09706a72beaa9d88baafaa834a74f27823bc5306df0d3de38763480bc11252c2b11b6fa4d1f28e26aa3a1867072f21f5f3725b16482a236bc366b3bc4f1a406e740b8fb607e7326d88db61989de15753f4527f1d0443a81674423682e80b0f472f049a1de3d1169fc441cb1bc3a31909e14479c96c3eae448ad61af2',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="124"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
    }
    data = {
        "input": text,
        "voice": voice_id,
        "format": "mp3",
        "mimeCode": "audio/mpeg",
        "emotion": "",
        "speed": 1,
        "quality": "premium"
    }
    response = requests.post(url, headers=headers, json=data)
    logger.info(f"TTS generation response status code: {response.status_code}")
    return response.content

st.title("Voice Cloning TTS App")

uploaded_file = st.file_uploader("Upload an MP3 file", type="mp3")

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)
    logger.info(f"File details: {file_details}")
    
    # Save the uploaded file temporarily
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Get upload URL
    upload_info = get_upload_url(uploaded_file.name, uploaded_file.size)
    
    # Upload file
    if upload_file(upload_info['url'], upload_info['fields'], uploaded_file.name):
        st.success("File uploaded successfully!")
        
        # Start workflow
        workflow_response = start_workflow(upload_info['file_url'])
        st.write("Workflow Response:", workflow_response)
        
        # Extract voice_id more safely
        voice_id = None
        if isinstance(workflow_response, dict):
            for key, value in workflow_response.items():
                if isinstance(value, dict) and 'step_results' in value:
                    try:
                        voice_id = value['step_results']['cmMxi']['return_value']['cmMwu']['return_value']['data']['_p_body.id']
                        break
                    except KeyError:
                        continue

        if voice_id:
            st.write(f"Voice ID: {voice_id}")
            logger.info(f"Extracted Voice ID: {voice_id}")
            
            # Generate TTS
            text_input = st.text_input("Enter text for TTS:")
            if st.button("Generate TTS"):
                audio_content = generate_tts(voice_id, text_input)
                st.audio(audio_content, format='audio/mp3')
        else:
            st.error("Failed to extract Voice ID. Please try again.")
            logger.error("Failed to extract Voice ID from workflow response")
    else:
        st.error("Failed to upload file.")
        logger.error("Failed to upload file")

    # Clean up the temporary file
    os.remove(uploaded_file.name)
    logger.info(f"Removed temporary file: {uploaded_file.name}")

# Display logs in Streamlit
st.text_area("Logs", value='\n'.join(streamlit_handler.logs), height=300)
