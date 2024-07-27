import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class CloudflareBypass:
    def __init__(self):
        self.page = None
        self.conversation_id = None

    async def init_browser(self):
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 720},
            device_scale_factor=1,
        )
        self.page = await context.new_page()
        await self.page.goto("https://pi.ai/talk")
        await asyncio.sleep(5)  # Wait for the page to load

    async def init_conversation(self):
        if not self.page:
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

            self.conversation_id = response['mainConversation']['sid']
            return self.conversation_id
        except Exception as e:
            print(f"Error in init_conversation: {str(e)}")
            raise

    async def get_voice(self, text, voice):
        if not self.conversation_id:
            await self.init_conversation()

        try:
            response = await self.page.evaluate(f"""
                async () => {{
                    const chatResponse = await fetch("https://pi.ai/api/chat", {{
                        method: "POST",
                        headers: {{
                            "Accept": "text/event-stream",
                            "Content-Type": "application/json",
                            "X-Api-Version": "3"
                        }},
                        body: JSON.stringify({{
                            conversation: "{self.conversation_id}",
                            text: "{text}"
                        }})
                    }});
                    const chatData = await chatResponse.text();
                    const lines = chatData.split('\\n');
                    let receivedSid;
                    for (const line of lines) {{
                        if (line.startsWith('event: received')) {{
                            const receivedData = JSON.parse(line.split('data: ')[1]);
                            receivedSid = receivedData.sid;
                            break;
                        }}
                    }}
                    if (!receivedSid) throw new Error("No received SID found");
                    const voiceResponse = await fetch(`https://pi.ai/api/chat/voice?mode=eager&voice=voice{voice}&messageSid=${{receivedSid}}`, {{
                        method: "GET",
                        headers: {{
                            "Range": "bytes=0-"
                        }}
                    }});
                    const voiceBuffer = await voiceResponse.arrayBuffer();
                    return new Uint8Array(voiceBuffer);
                }}
            """)
            return response
        except Exception as e:
            print(f"Error in get_voice: {str(e)}")
            raise

    async def close(self):
        if self.page:
            await self.page.context.close()
