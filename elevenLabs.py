import requests
import json
import os
from dotenv import load_dotenv
import shutil


class ElevenLabs:

    def __init__(self):
        self.apikey = os.getenv('ELEVENLABS_TOKEN')


    def addVoice(self, voiceName, accent, description, tempPath):
        url = "https://api.elevenlabs.io/v1/voices/add"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        data = {
            'name': voiceName,
            'labels': '{"accent": "' +str(accent) +'"}',
            'description': description
        }

        files = []

        for file_name in os.listdir(tempPath):
            file_path = os.path.join(tempPath, file_name)
            files.append(('files', (file_name, open(file_path, 'rb'), 'audio/mpeg')))

        response = requests.post(url, headers=headers, data=data, files=files)
        
        return json.loads(response.text)['voice_id']


    def editVoice(self,voiceId, voiceName, accent, description, tempPath):
        url = f"https://api.elevenlabs.io/v1/voices/{voiceId}/edit"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        data = {
            'name': voiceName,
            'labels': '{"accent": "' +str(accent) +'"}',
            'description': description
        }
            
        files = []

        if tempPath:
            for file_name in os.listdir(tempPath):
                file_path = os.path.join(tempPath, file_name)
                files.append(('files', (file_name, open(file_path, 'rb'), 'audio/mpeg')))

        requests.post(url, headers=headers, data=data, files=files)


    def textToSpeech(self, text, voice_id, path):

        response = requests.get(
                        "https://api.elevenlabs.io/v1/voices/settings/default",
                        headers={ "Accept": "application/json" }
                    ).json()

        stability, similarity_boost = response["stability"], response["similarity_boost"]
        
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
                "stability": stability,
                "similarity_boost": similarity_boost
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


    def getMaxVoiceCount(self):
        url = "https://api.elevenlabs.io/v1/user/subscription"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        response = requests.get(url, headers=headers)
        return json.loads(response.text)['voice_limit']


    def deleteVoice(self, voiceId):
        url = "https://api.elevenlabs.io/v1/voices/" + str(voiceId)

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        response = requests.delete(url, headers=headers)
        return json.loads(response.text)


    def getVoices(self):
        url = "https://api.elevenlabs.io/v1/voices"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        response = requests.get(url, headers=headers)
        voices = json.loads(response.text)['voices']
        return [voice for voice in voices if voice['category'] != 'premade'] 


    def getAudioFromSample(self, voiceId, sampleId, path):

        dir_path, file_name = os.path.split(path)

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        
        url = f"https://api.elevenlabs.io/v1/voices/{voiceId}/samples/{sampleId}/audio"

        headers = {
            "Accept": "audio/*",
            "xi-api-key": self.apikey
        }

        response = requests.get(url, headers=headers)

        CHUNK_SIZE = 1024

        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
        
        return


    def getVoice(self, voiceId):
        url = f"https://api.elevenlabs.io/v1/voices/{voiceId}"

        headers = {
            "Accept": "application/json",
            "xi-api-key": self.apikey
        }

        response = requests.get(url, headers=headers)
        voice = json.loads(response.text)
        if len(voice['samples'])== 0:
            return None
        return voice