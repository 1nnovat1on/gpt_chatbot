# gpt_chatbot
This chatbot allows you to use your microphone to communicate with GPT-3. It also uses ElevenLabs API to respond with a realistic voice. API keys for OpenAI and ElevenLabs are required. Tested on Windows

Feel free to reach out with questions. If you do not have ElevenLabs API, you can use the included code for Windows native TTS.
            
            Comment this line out (ln 148)
            # ----- ElevenLabs
            # voiceTest.speak(response)
            
            and this one needs to be active
            # ----- Windows TTS
            talk(response)
