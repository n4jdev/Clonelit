import asyncio
import json
import aiohttp
from playwright.async_api import async_playwright
import os

class PiAIClient:
    def __init__(self):
        self.host = 'pi.ai'
        self.browser = None
        self.context = None
        self.page = None

    async def init_browser(self):
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                viewport={"width": 1280, "height": 720},
                device_scale_factor=1,
            )
            self.page = await self.context.new_page()
            await self.page.goto(f"https://{self.host}/talk")
            await asyncio.sleep(5)  # Wait for the page to load

    # ... (rest of the code remains the same)

    async def init_conversation(self):
        await self.init_browser()
        try:
            response = await self.page.evaluate("""
                async () => {
                    const response = await fetch("https://pi.ai/api/chat/start", {
                        method: "POST",
                        headers: {
                            "accept": "application/json",
                            "X-Api-Version": "3",
                            "content-type": "application/json"
                        },
                        body: "{}"
                    });
                    return await response.json();
                }
            """)
            
            if not isinstance(response, dict) or 'mainConversation' not in response:
                raise Exception("Failed to init conversation")

            return response['mainConversation']['sid']
        except Exception as e:
            print(f"Error in init_conversation: {str(e)}")
            raise

    async def send_message(self, conversation_id, message):
        if not self.page:
            await self.init_browser()

        try:
            response = await self.page.evaluate(f"""
                async () => {{
                    const response = await fetch("https://pi.ai/api/chat", {{
                        method: "POST",
                        headers: {{
                            "Accept": "text/event-stream",
                            "Content-Type": "application/json",
                            "X-Api-Version": "3"
                        }},
                        body: JSON.stringify({{
                            conversation: "{conversation_id}",
                            text: "{message}"
                        }})
                    }});
                    return await response.text();
                }}
            """)

            received_sid = None
            for line in response.split('\n'):
                if line.startswith('event: received'):
                    received_data = json.loads(next(line for line in response.split('\n') if line.startswith('data:')).split('data: ')[1])
                    received_sid = received_data.get('sid')
                    break

            return {'received_sid': received_sid}
        except Exception as e:
            print(f"Error in send_message: {str(e)}")
            return None

    async def get_voice(self, message_sid, voice_id):
        cookies = await self.context.cookies()
        cookie_string = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'authority': 'pi.ai',
            'accept-language': 'en-US,en;q=0.9',
            'range': 'bytes=0-',
            'referer': 'https://pi.ai/talk',
            'sec-ch-ua': '"Not-A.Brand";v="99", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'audio',
            'sec-fetch-mode': 'no-cors',
            'sec-fetch-site': 'same-origin',
            'Cookie': cookie_string
        }

        url = f'https://{self.host}/api/chat/voice?mode=eager&voice=voice{voice_id}&messageSid={message_sid}'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                while True:
                    chunk = await response.content.read(4096)
                    if not chunk:
                        break
                    yield chunk

    async def close(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.context = None
            self.page = None
