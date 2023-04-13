import requests
import json
import os

class ElevenLabs:

    def __init__(self,token):
        self.apikey = token

    def addVoice(self, path, name, accent):
        url = "https://api.elevenlabs.io/v1/voices/add"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        data = {
            'name': name,
            'labels': '{"accent": "' +str(accent) +'"}',
            'description': 'Voice description'
        }

        files = []

        for file_name in os.listdir(path):
            file_path = os.path.join(path, file_name)
            files.append(('files', (file_name, open(file_path, 'rb'), 'audio/mpeg')))

        response = requests.post(url, headers=headers, data=data, files=files)
        
        return json.loads(response.text)['voice_id']

    def textToSpeech(self, text, voice_id, path):
        
        dir_path, file_name = os.path.split(path)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/" + str(voice_id) + "/stream"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.apikey
        }

        data = {
            "text": text,
            "voice_settings": {
                "stability": 0,
                "similarity_boost": 0
            }
        }

        response = requests.post(url, json=data, headers=headers, stream=True)

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        
        return

    def getCharCountResetDate(self):
        url = "https://api.elevenlabs.io/v1/user/subscription"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)['next_character_count_reset_unix']

    def deleteVoicesNotInDb(self, voicesInDb):
        return