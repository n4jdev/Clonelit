import streamlit as st
import requests
import json
import base64
import io

def get_upload_url(file_name, file_size):
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
    return response.json()

def upload_file(upload_url, fields, file_content):
    response = requests.post(
        upload_url,
        data=fields,
        files={'file': ('voice_cloning', file_content, 'audio/mpeg')}
    )
    return response.status_code == 204

def start_workflow(file_url):
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
        'x-bubble-fiber-id': '1722237867919x598363094394157200',
        'x-bubble-pl': '1722237591965x1002',
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
            "run_id": "1722237867910x800700790731605900",
            "server_call_id": "1722237867918x144831640779072420",
            "item_id": "cmMxd",
            "element_id": "cmMxX",
            "uid_generator": {"timestamp": 1722237867910, "seed": 962217465675474300},
            "random_seed": 0.20947760161398143,
            "current_date_time": 1722237867610,
            "current_wf_params": {}
        }],
        "timezone_offset": -480,
        "timezone_string": "Asia/Manila",
        "user_id": "1722234365445x688391142658434600"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def generate_tts(voice_id, text):
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
    return response.content

st.title("Voice Cloning TTS App")

uploaded_file = st.file_uploader("Upload your voice sample (MP3)", type="mp3")

if uploaded_file is not None:
    file_content = uploaded_file.read()
    file_size = len(file_content)
    
    # Step 1: Get upload URL
    upload_info = get_upload_url(uploaded_file.name, file_size)
    
    # Step 2: Upload file
    if upload_file(upload_info['url'], upload_info['fields'], file_content):
        st.success("Voice sample uploaded successfully!")
        
        # Step 3: Start workflow
        workflow_response = start_workflow(upload_info['file_url'])
        
        # Extract the voice ID from the correct path in the response
        try:
            server_call_id = list(workflow_response.keys())[0]  # Get the dynamic server call ID
            voice_id = workflow_response[server_call_id]['step_results']['cmMxi']['return_value']['cmMwu']['return_value']['data']['_p_body.id']
            st.success(f"Voice ID obtained: {voice_id}")
            
            # Step 4: Generate TTS
            text_input = st.text_area("Enter the text you want to convert to speech:")
            if st.button("Generate TTS"):
                if text_input:
                    tts_audio = generate_tts(voice_id, text_input)
                    st.audio(tts_audio, format="audio/mp3")
                else:
                    st.warning("Please enter some text to convert to speech.")
        except KeyError as e:
            st.error(f"Error extracting voice ID from the API response. Please check the API response structure: {e}")
            st.json(workflow_response)  # Display the full response for debugging
    else:
        st.error("Failed to upload voice sample.")

st.write("Note: This app uses external APIs and may not work if the APIs are changed or become unavailable.")
