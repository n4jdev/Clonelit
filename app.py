import streamlit as st
import asyncio
import json
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import subprocess
import sys

# Install required packages
subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "playwright"])

# Install Playwright browsers
subprocess.check_call([sys.executable, "-m", "playwright", "install"])

class Tools:
    debug = True

    @staticmethod
    def debug_print(message: str, data: object = None) -> None:
        if Tools.debug:
            print(f"[DEBUG] {message}")
            if data is not None:
                print(f"[DEBUG DATA] {data}")

class Prompt:
    def __init__(self, text: str):
        self.text = text

class Conversation:
    def __init__(self):
        self.conversation_id = None
        self.cookie = None
        self.current_text = ''
        self.ended = False
        self.page = None

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

        # Perform human-like interactions
        await self.random_scroll()
        await self.random_mouse_move()

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
            
            Tools.debug_print("initConversation result", response)

            if not isinstance(response, dict) or 'mainConversation' not in response:
                raise Exception("Failed to init conversation")

            self.conversation_id = response['mainConversation']['sid']
            self.cookie = await self.page.context.cookies()
            return {
                'conversation_id': self.conversation_id,
                'cookie': self.cookie,
            }
        except Exception as e:
            Tools.debug_print(f"Error in init_conversation: {str(e)}")
            raise

    async def ask(self, message: Prompt, callback = None):
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
                            conversation: "{self.conversation_id}",
                            text: "{message.text}"
                        }})
                    }});
                    return await response.text();
                }}
            """)

            self.current_text = ''
            for line in response.split('\n'):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if isinstance(data, dict) and 'text' in data:
                            self.current_text += data['text']
                            if callback:
                                callback(self.current_text, data['text'])
                    except json.JSONDecodeError:
                        pass

            if not self.current_text:
                self.ended = True
                self.current_text = "I'm sorry, please start a new conversation!"

            if callback:
                callback(self.current_text, self.current_text)

            return self.current_text
        except Exception as e:
            Tools.debug_print(f"Error in ask: {str(e)}")
            self.ended = True
            return "An error occurred. Please try again."

    async def random_scroll(self):
        await self.page.evaluate("""
            () => {
                window.scrollTo(0, Math.floor(Math.random() * document.body.scrollHeight));
            }
        """)
        await asyncio.sleep(random.uniform(1, 3))

    async def random_mouse_move(self):
        await self.page.mouse.move(
            random.randint(0, 1280),
            random.randint(0, 720)
        )
        await asyncio.sleep(random.uniform(0.5, 1.5))

    def is_ended(self):
        return self.ended

class Client:
    @staticmethod
    async def create_conversation():
        conversation = Conversation()
        await conversation.init_conversation()
        return conversation

async def get_ai_response(conversation, user_input):
    prompt = Prompt(user_input)
    response = await conversation.ask(prompt)
    return response

def main():
    st.title("Pi AI Chatbot")

    # Initialize session state
    if 'conversation' not in st.session_state:
        st.session_state.conversation = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input
    if user_input := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # Create or get conversation
            if st.session_state.conversation is None or st.session_state.conversation.is_ended():
                with st.spinner("Starting a new conversation..."):
                    st.session_state.conversation = asyncio.run(Client.create_conversation())

            # Get AI response
            with st.spinner("AI is thinking..."):
                full_response = asyncio.run(get_ai_response(st.session_state.conversation, user_input))

            message_placeholder.markdown(full_response)

        # Add AI response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()
