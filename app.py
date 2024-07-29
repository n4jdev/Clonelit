import streamlit as st
import requests
import json
import base64
import os
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for session management
SESSION_COOKIES = None
X_BUBBLE_FIBER_ID = None

def update_session_info(response):
    global SESSION_COOKIES, X_BUBBLE_FIBER_ID
    SESSION_COOKIES = response.cookies
    X_BUBBLE_FIBER_ID = response.headers.get('x-bubble-fiber-id')

def get_headers():
    return {
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
        'x-bubble-fiber-id': X_BUBBLE_FIBER_ID,
        'x-bubble-pl': '1722237591965x1002',
        'x-bubble-r': 'https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice',
        'x-requested-with': 'XMLHttpRequest',
    }

def refresh_session():
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/api/1.1/wf/refresh_session"
    response = requests.post(url, headers=get_headers(), cookies=SESSION_COOKIES)
    update_session_info(response)
    return response.json()

def get_upload_url(file_name, file_size):
    logger.info(f"Getting upload URL for file: {file_name}, size: {file_size}")
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/fileupload/geturl"
    headers = get_headers()
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
            "current_date_time": int(time.time() * 1000),
            "timezone_offset": -480,
            "timezone_string": "Asia/Manila",
            "inputs_must_be_valid": False,
            "current_wf_params": {}
        },
        "name": file_name,
        "size": file_size,
        "content_type": "audio/mpeg"
    }
    response = requests.post(url, headers=headers, json=data, cookies=SESSION_COOKIES)
    update_session_info(response)
    logger.info(f"Upload URL response: {response.text}")
    return response.json()

def upload_file(upload_url, fields, file_path):
    logger.info(f"Uploading file: {file_path}")
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'audio/mpeg')}
        response = requests.post(upload_url, data=fields, files=files)
    logger.info(f"Upload response status code: {response.status_code}")
    return response.status_code == 204

def start_workflow(file_url, max_retries=3):
    for attempt in range(max_retries):
        logger.info(f"Starting workflow with file URL: {file_url} (Attempt {attempt + 1})")
        url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/workflow/start"
        headers = get_headers()
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
                "run_id": "1722234365445x688391142658434600",
                "server_call_id": "1722234365445x688391142658434600",
                "item_id": "cmMxd",
                "element_id": "cmMxX",
                "uid_generator": {"timestamp": int(time.time() * 1000), "seed": int(time.time() * 1000000)},
                "random_seed": 0.20947760161398143,
                "current_date_time": int(time.time() * 1000),
                "current_wf_params": {}
            }],
            "timezone_offset": -480,
            "timezone_string": "Asia/Manila",
            "user_id": "1722234365445x688391142658434600"
        }
        response = requests.post(url, headers=headers, json=data, cookies=SESSION_COOKIES)
        update_session_info(response)
        result = response.json()
        logger.info(f"Workflow response: {result}")
        
        if "error_class" in result and result["error_class"] == "Unauthorized" and result["message"] == "EXPIRED_SESSION":
            logger.info("Session expired. Refreshing session and retrying...")
            refresh_session()
        else:
            return result
    
    logger.error("Max retries reached. Unable to start workflow.")
    return None

# ... (rest of the code remains the same)

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
        if workflow_response:
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
            st.error("Failed to start workflow. Please try again.")
    else:
        st.error("Failed to upload file.")
        logger.error("Failed to upload file")

    # Clean up the temporary file
    os.remove(uploaded_file.name)
    logger.info(f"Removed temporary file: {uploaded_file.name}")

# Display logs in Streamlit
if 'log_output' not in st.session_state:
    st.session_state.log_output = []

class StreamlitHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        st.session_state.log_output.append(log_entry)

streamlit_handler = StreamlitHandler()
streamlit_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(streamlit_handler)

st.text_area("Logs", value='\n'.join(st.session_state.log_output), height=300)
