from cloudflare_bypass import CloudflareBypass

class TTSService:
    def __init__(self):
        self.cloudflare_bypass = CloudflareBypass()

    async def generate_speech(self, text, voice):
        try:
            audio_data = await self.cloudflare_bypass.get_voice(text, voice)
            chunk_size = 4096
            for i in range(0, len(audio_data), chunk_size):
                yield bytes(audio_data[i:i+chunk_size])
        except Exception as e:
            print(f"Error in generate_speech: {str(e)}")
            yield b''
        finally:
            await self.cloudflare_bypass.close()
