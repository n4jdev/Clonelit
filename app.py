import streamlit as st
import requests
import json
import io
import base64

def get_upload_url(file_name, file_size):
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/fileupload/geturl"
    headers = {
        'authority': 'playhttexttospeechdemo.bubbleapps.io',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    data = {
        "public": True,
        "service": "bubble",
        "timezone_string": "Asia/Manila",
        "name": file_name,
        "size": file_size,
        "content_type": "audio/x-m4a"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def upload_file(upload_url, fields, file):
    response = requests.post(upload_url, data=fields, files={'file': file})
    return response.status_code == 204

def start_workflow(file_url):
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/workflow/start"
    headers = {
        'authority': 'playhttexttospeechdemo.bubbleapps.io',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    data = {
        "wait_for": [],
        "app_last_change": "19875058729",
        "client_breaking_revision": 5,
        "calls": [{
            "client_state": {
                "element_instances": {
                    "cmMxX": {
                        "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMxX",
                        "parent_element_id": "cmMuK"
                    }
                },
                "element_state": {
                    "1348695171700984260__LOOKUP__ElementInstance::cmMxX": {
                        "is_visible": True,
                        "value_that_is_valid": file_url,
                        "value": file_url
                    }
                }
            },
            "run_id": "1722307769078x576144250376689800",
            "server_call_id": "1722307769083x636360784032498700",
            "item_id": "cmMxd",
            "element_id": "cmMxX",
        }],
        "timezone_offset": -480,
        "timezone_string": "Asia/Manila",
        "user_id": "1722303920846x322366301969347260"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def generate_tts(voice_id, text):
    url = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
    headers = {
        'authority': 'europe-west3-bubble-io-284016.cloudfunctions.net',
        'accept': '*/*',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer 8ccbf7cf6fdbfdaf509b29ac185d131d5928afa33b7ea216439ca60f8fc8d167fe7ac23843d74651bbabe15758bb01b0402369c8639ee3ffc1abe6adcd404b04bb70199773bbe672fe2567a05aadf7d7257b5ee00a05241057d7e08fbedbc8b59add5c15324cd7dc051f09d4e47fb1bfe255f8289adc0c078e0b454bf57d654f9736cab983340213519c694278f16239f06433c3b3500e7b0e7a663edd3c2b9e5bea159fa22ce6c3e2eba54e9c7d050f09706a72beaa9d88baafaa834a74f27823bc5306df0d3de38763480bc11252c2b11b6fa4d1f28e26aa3a1867072f21f5f3725b16482a236bc366b3bc4f1a406e740b8fb607e7326d88db61989de15753f4527f1d0443a81674423682e80b0f472f049a1de3d1169fc441cb1bc3a31909e14479c96c3eae448ad61af2',
        'content-type': 'application/json',
        'origin': 'https://playhttexttospeechdemo.bubbleapps.io',
        'referer': 'https://playhttexttospeechdemo.bubbleapps.io/',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    }
    data = {
        "input": text,
        "voice": voice_id,
        "format": "mp3",
        "mimeCode": "audio/mpeg",
        "speed": 1,
        "quality": "premium"
    }
    response = requests.post(url, headers=headers, json=data)
    return response.content

st.title("Voice Cloning TTS App")

uploaded_file = st.file_uploader("Upload your voice sample (MP3)", type="mp3")

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)

    # Step 1: Get upload URL
    upload_info = get_upload_url(uploaded_file.name, uploaded_file.size)
    
    # Step 2: Upload file
    if upload_file(upload_info['url'], upload_info['fields'], uploaded_file):
        st.success("File uploaded successfully!")

        # Step 3: Start workflow
        workflow_response = start_workflow(upload_info['file_url'])
        voice_id = workflow_response["1722307769083x636360784032498700"]["step_results"]["cmMxi"]["return_value"]["cmMwu"]["return_value"]["data"]["_p_body.id"]
        st.write(f"Voice ID: {voice_id}")

        # Step 4: Generate TTS
        text_input = st.text_area("Enter text to convert to speech:")
        if st.button("Generate TTS"):
            audio_content = generate_tts(voice_id, text_input)
            
            # Convert audio content to base64
            audio_base64 = base64.b64encode(audio_content).decode()
            
            # Display audio player
            st.audio(audio_content, format='audio/mp3')
            
            # Provide download link
            st.markdown(f'<a href="data:audio/mp3;base64,{audio_base64}" download="generated_speech.mp3">Download MP3</a>', unsafe_allow_html=True)

else:
    st.info("Please upload an MP3 file to start.")
