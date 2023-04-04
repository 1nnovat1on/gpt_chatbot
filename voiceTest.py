#--deprecated. maybe you can fix it or make it go faster?
# We need the audio to play more quickly, and maybe stream instead of save locally
    
import requests
import playsound
import os



def speak(text = None):
    url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    voice_id = "yoZ06aMxZJJ28mfd3POQ"
    api_key = os.getenv('elkey')

    data = {
    "text": text
    }

    headers = {
        "Content-Type": "application/json",
        "xi-api-key" : api_key
    }

    response = requests.post(url.format(voice_id=voice_id), headers=headers, json=data)

    if response.status_code == 200:

        with open('p.mp3', 'wb') as f:
            f.write(response.content)

        playsound.playsound('p.mp3')
        os.remove("p.mp3")

    else:
        print("Request failed with status code:", response.status_code)
