import streamlit as st
import requests
import json

# Function to upload file and get URL
def upload_file(file):
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/fileupload/geturl"
    headers = {
        "authority": "playhttexttospeechdemo.bubbleapps.io",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "origin": "https://playhttexttospeechdemo.bubbleapps.io",
        "referer": "https://playhttexttospeechdemo.bubbleapps.io/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "x-bubble-breaking-revision": "5",
        "x-bubble-fiber-id": "1722307766856x931152043432026000",
        "x-bubble-pl": "1722307752719x826",
        "x-bubble-r": "https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice",
        "x-requested-with": "XMLHttpRequest"
    }
    data = {
        "public": True,
        "service": "bubble",
        "timezone_string": "Asia/Manila",
        "serialized_context": {
            "client_state": {
                "element_instances": {
                    "cmMuK": {
                        "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMuK",
                        "parent_element_id": "cmMsT"
                    },
                    "cmMxX": {
                        "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMxX",
                        "parent_element_id": "cmMuK"
                    }
                },
                "element_state": {
                    "1348695171700984260__LOOKUP__ElementInstance::cmMuK": {
                        "group_data": None
                    }
                },
                "other_data": {
                    "Current Page Scroll Position": 0,
                    "Current Page Width": 360
                },
                "cache": {},
                "exists": {}
            },
            "element_id": "cmMxX",
            "current_date_time": 1722307766685,
            "timezone_offset": -480,
            "timezone_string": "Asia/Manila",
            "inputs_must_be_valid": False,
            "current_wf_params": {}
        },
        "name": file.name,
        "size": file.size,
        "content_type": "audio/x-m4a"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# Function to upload file to S3
def upload_to_s3(file, s3_data):
    url = "https://s3.amazonaws.com/appforest_uf"
    headers = {
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryZKakOLy4HDTNHC2V",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "referrer": "https://playhttexttospeechdemo.bubbleapps.io/",
        "referrerPolicy": "origin"
    }
    files = {
        "file": (file.name, file, "audio/mpeg")
    }
    data = {
        "key": s3_data["fields"]["key"],
        "x-amz-meta-appname": "playhttexttospeechdemo",
        "x-amz-meta-app-version": "test",
        "Content-Type": "audio/mpeg",
        "x-amz-meta-scheduled-id": s3_data["fields"]["x-amz-meta-scheduled-id"],
        "acl": "public-read",
        "bucket": "appforest_uf",
        "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
        "X-Amz-Credential": s3_data["fields"]["X-Amz-Credential"],
        "X-Amz-Date": s3_data["fields"]["X-Amz-Date"],
        "Policy": s3_data["fields"]["Policy"],
        "X-Amz-Signature": s3_data["fields"]["X-Amz-Signature"]
    }
    response = requests.post(url, headers=headers, files=files, data=data)
    return response.status_code == 204

# Function to start workflow
def start_workflow(file_url, cookies):
    url = "https://playhttexttospeechdemo.bubbleapps.io/version-test/workflow/start"
    headers = {
        "authority": "playhttexttospeechdemo.bubbleapps.io",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "cookie": cookies,
        "origin": "https://playhttexttospeechdemo.bubbleapps.io",
        "referer": "https://playhttexttospeechdemo.bubbleapps.io/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "x-bubble-breaking-revision": "5",
        "x-bubble-fiber-id": "1722307769084x485968983730036740",
        "x-bubble-pl": "1722307752719x826",
        "x-bubble-r": "https://playhttexttospeechdemo.bubbleapps.io/version-test/cloned-voice",
        "x-requested-with": "XMLHttpRequest"
    }
    data = {
        "wait_for": [],
        "app_last_change": "19875058729",
        "client_breaking_revision": 5,
        "calls": [
            {
                "client_state": {
                    "element_instances": {
                        "cmMxX": {
                            "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMxX",
                            "parent_element_id": "cmMuK"
                        },
                        "cmMsq": {
                            "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMsq",
                            "parent_element_id": "cmMsk"
                        },
                        "cmMuK": {
                            "dehydrated": "1348695171700984260__LOOKUP__ElementInstance::cmMuK",
                            "parent_element_id": "cmMsT"
                        }
                    },
                    "element_state": {
                        "1348695171700984260__LOOKUP__ElementInstance::cmMxX": {
                            "is_visible": True,
                            "value_that_is_valid": file_url,
                            "value": file_url
                        },
                        "1348695171700984260__LOOKUP__ElementInstance::cmMuK": {
                            "group_data": None
                        }
                    },
                    "other_data": {
                        "Current Page Scroll Position": 0,
                        "Current Page Width": 360
                    },
                    "cache": {},
                    "exists": {}
                },
                "run_id": cookies.split("|")[0],
                "server_call_id": cookies.split("|")[1],
                "item_id": "cmMxd",
                "element_id": "cmMxX",
                "uid_generator": {
                    "timestamp": 1722307769078,
                    "seed": 810702303449379000
                },
                "random_seed": 0.09531869096932688,
                "current_date_time": 1722307768913,
                "current_wf_params": {}
            }
        ],
        "timezone_offset": -480,
        "timezone_string": "Asia/Manila",
        "user_id": cookies.split("|")[2]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# Function to generate TTS
def generate_tts(voice_id, text):
    url = "https://europe-west3-bubble-io-284016.cloudfunctions.net/get-stream"
    headers = {
        "authority": "europe-west3-bubble-io-284016.cloudfunctions.net",
        "accept": "*/*",
        "accept-language": "en-PH,en-US;q=0.9,en;q=0.8",
        "authorization": "Bearer 8ccbf7cf6fdbfdaf509b29ac185d131d5928afa33b7ea216439ca60f8fc8d167fe7ac23843d74651bbabe15758bb01b0402369c8639ee3ffc1abe6adcd404b04bb70199773bbe672fe2567a05aadf7d7257b5ee00a05241057d7e08fbedbc8b59add5c15324cd7dc051f09d4e47fb1bfe255f8289adc0c078e0b454bf57d654f9736cab983340213519c694278f16239f06433c3b3500e7b0e7a663edd3c2b9e5bea159fa22ce6c3e2eba54e9c7d050f09706a72beaa9d88baafaa834a74f27823bc5306df0d3de38763480bc11252c2b11b6fa4d1f28e26aa3a1867072f21f5f3725b16482a236bc366b3bc4f1a406e740b8fb607e7326d88db61989de15753f4527f1d0443a81674423682e80b0f472f049a1de3d1169fc441cb1bc3a31909e14479c96c3eae448ad61af2",
        "content-type": "application/json",
        "origin": "https://playhttexttospeechdemo.bubbleapps.io",
        "referer": "https://playhttexttospeechdemo.bubbleapps.io/",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    data = {
        "input": text,
        "voice": voice_id,
        "format": "mp3",
        "mimeCode": "audio/mpeg",
        "speed": 1,
        "quality": "premium"
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.content

# Streamlit App
def main():
    st.title("TTS Voice Cloning App")
    
    uploaded_file = st.file_uploader("Upload an .mp3 audio file", type=["mp3"])
    
    if uploaded_file is not None:
        st.write("File uploaded successfully!")
        
        # Step 1: Upload file and get URL
        s3_data = upload_file(uploaded_file)
        file_url = s3_data["file_url"]
        
        # Step 2: Upload file to S3
        if upload_to_s3(uploaded_file, s3_data):
            st.write("File uploaded to S3 successfully!")
            
            # Step 3: Start workflow
            cookies = "playhttexttospeechdemo_test_u2main=bus|1722303920846x322366301969347260|1722303920867x234219269417406100; playhttexttospeechdemo_test_u2main.sig=qg3jhxENBXCklzRicwfPxg2pmbQ; playhttexttospeechdemo_u1_testmain=1722303920846x322366301969347260"
            workflow_response = start_workflow(file_url, cookies)
            voice_id = workflow_response["1722307769083x636360784032498700"]["step_results"]["cmMxi"]["return_value"]["cmMwu"]["return_value"]["data"]["_p_body.id"]
            
            st.write("Workflow started successfully!")
            
            # Step 4: Generate TTS
            text = st.text_area("Enter the text you want to convert to speech")
            if st.button("Generate TTS"):
                tts_audio = generate_tts(voice_id, text)
                st.audio(tts_audio, format="audio/mpeg")

if __name__ == "__main__":
    main()
