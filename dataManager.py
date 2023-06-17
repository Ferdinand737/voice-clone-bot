from database import DataBase
from elevenLabs import ElevenLabs
import os
import shutil
import json



class DataManager:

    def __init__(self):
        self.eLabs = ElevenLabs()
        self.db = DataBase()

    
    def getVoice(self, serverId, voiceName):

        print(f"Getting voice {voiceName}...")

        dbVoice = self.db.getVoice(serverId, voiceName)

        if dbVoice is None:
            #The voice is missing from the database
            print(f"Voice '{voiceName}' not found in database. Attempting to retrieve from ElevenLabs...")
            
            voices = self.eLabs.getVoices()

            if len(voices) == 0:
                print("Unable to retrieve voice because there are no voices on ElevenLabs.")
                return None

            for voice in voices:

                try:
                    voiceDesc = json.loads(voice['description'])
                except:

                    if voice['name'] == voiceName:
                        print(f"{voice['name']} has invalid description on ElevenLabs.")                        
                        return None
                
                    print(f"{voice['name']} has invalid description on ElevenLabs.")

                    continue

                if voice['name'] == voiceName or voiceDesc['shortcut'] == voiceName:
                        
                    if voiceDesc['server_id'] == serverId or voiceDesc['server_id'] == None:
                        #The voice exists on ElevenLabs
                        serverId = None if voiceDesc['server_id'] == "public" else voiceDesc['server_id']

                        print(f"Found {voiceName} on ElevenLabs!\nAdding {voiceName} to database...")
                        
                        self.db.addVoice(voice['voice_id'], voice['name'], voiceDesc['shortcut'], voice['labels']['accent'],serverId, voiceDesc['user_id'], voiceDesc['path'])
                        
                        if not os.path.exists(f"voices/{voice['voice_id']}"):
                            #The files Local files are missing
                            print(f"Missing local voice samples for {voiceName}\nDownloading from ElevenLabs...")
                            for sample in voice['samples']:
                                path =  os.path.join(voiceDesc['path'],sample['file_name'])
                                self.eLabs.getAudioFromSample(voice['voice_id'], sample['sample_id'], path)

                            print(f"Successfully downloaded samples for {voiceName}!")

                        print(f"Successfully restored {voiceName}!")
                        return self.db.getVoice(serverId, voiceName)
                    else:
                        print(f"Could not find {voiceName} on ElevenLabs.")
                        return None
            print(f"Could not restore {voiceName}")
            return None
        
        eLabsVoice = self.eLabs.getVoice(dbVoice['voice_id'])

        if eLabsVoice is None:
            #The voice is missing from ElevenLabs
            print(f"{voiceName} not found on ElevenLabs\nAttempting to restore...")

            if not os.path.exists(dbVoice['path']):
                print(f"Unable to restore {voiceName} because no local samples were found\nDeleting {voiceName} from database.")
                self.db.deleteVoice(dbVoice['voice_id'])
                return None
            

            description = {
                "shortcut": dbVoice['shortcut'],
                "server_id": dbVoice['server_id'],
                "user_id": dbVoice['user_id'],
                "path": dbVoice['path']
            }

            self.deleteUnpopularVoice(dbVoice['voice_id'])

            print(f"Adding {voiceName} to ElevenLabs...")
            newVoiceId = self.eLabs.addVoice(dbVoice['name'], dbVoice['accent'], json.dumps(description), dbVoice['path'])

            newPath = f"voices/{dbVoice['server_id']}/{newVoiceId}"

            if not os.path.exists(newPath):
                os.makedirs(newPath)

            for filename in os.listdir(dbVoice['path']):
                if os.path.isfile(os.path.join(dbVoice['path'], filename)):
                    shutil.move(os.path.join(dbVoice['path'], filename), newPath)
                    
            shutil.rmtree(dbVoice['path'])


            self.db.updateVoiceId(dbVoice['voice_id'], newVoiceId, newPath)
            print(f"Successfully restored {voiceName}!")
            return self.db.getVoiceById(newVoiceId)

        else:
            folderPath = dbVoice['path']
            if not os.path.exists(folderPath):
                #There is a voice on ElevenLabs and in the Database but no local files
                print("ElevenLabs voice found")
                print(f"Missing local voice samples for {voiceName}\nDownloading from ElevenLabs...")
                for sample in eLabsVoice['samples']:
                    filePath =  os.path.join(folderPath, sample['file_name'])
                    self.eLabs.getAudioFromSample(eLabsVoice['voice_id'], sample['sample_id'], filePath)

                print(f"Successfully downloaded samples for {voiceName}!")
                print(f"Successfully restored {voiceName}!")
                return dbVoice
        
        print("Voice retrieved without restoration!")
        return dbVoice


    def addVoice(self, voiceName, accent, serverId, userId, tempPath):
        print(f"Adding voice {voiceName}...")

        shortcut = self.getShortcut(voiceName)

        self.deleteUnpopularVoice("@TeamOnionGaming")

        voiceId = self.eLabs.addVoice(voiceName, accent,'',tempPath)

        path = f"voices/{serverId}/{voiceId}"

        if not os.path.exists(path):
            os.makedirs(path)

        for filename in os.listdir(tempPath):
            if os.path.isfile(os.path.join(tempPath, filename)):
                shutil.move(os.path.join(tempPath, filename), path)

        shutil.rmtree(tempPath)

        self.db.addVoice(voiceId, voiceName, shortcut, accent, serverId, userId, path)

        description = {
            "shortcut": shortcut,
            "server_id": serverId,
            "user_id": userId,
            "path": path
        }

        self.eLabs.editVoice(voiceId, voiceName, accent, json.dumps(description), None)
        
        print(f"Successfully added {voiceName}!")
        return self.db.getVoiceById(voiceId)
    

    def deleteUnpopularVoice(self, dontDeleteThisVoiceId):
        dontDeleteThese = [dontDeleteThisVoiceId]

        voices = self.eLabs.getVoices()
        voiceIds = [voice['voice_id'] for voice in voices]

        if len(voices) == self.eLabs.getMaxVoiceCount():
            unpopularVoiceID = self.db.getUnpopularVoice(dontDeleteThese)['voice_id']

            while unpopularVoiceID not in voiceIds:
                dontDeleteThese.append(unpopularVoiceID)
                unpopularVoiceID = self.db.getUnpopularVoice(dontDeleteThese)['voice_id']

            unpopularVoice = self.db.getVoiceById(unpopularVoiceID)
            print(f"Maximum voice count reached on ElevenLabs\nDeleting least used voice ({unpopularVoice['name']}) from ElevenLabs...")
            self.eLabs.deleteVoice(unpopularVoice['voice_id'])
            print(f"Successfully deleted {unpopularVoice['name']} from ElevenLabs!")


    def getShortcut(self, voiceName):
        shortcut = ""

        for char in voiceName: 
            if char.isupper():
                shortcut += char
        
        if len(shortcut)==0:
            shortcut += voiceName[0]
            shortcut += voiceName[len(voiceName)//2]

        return shortcut


    def textToSpeech(self, args, voiceId, userId, serverId, script):

        debug = script[:40].replace('\n','') + '...'

        print(f"Adding response ({debug}) to database...")
        path = self.db.addPrompt(args, voiceId, userId, serverId, script, len(script))['path']      

        parent_dir = os.path.dirname(path)

        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        print(f"Requesting audio file from ElevenLabs...")
        self.eLabs.textToSpeech(script, voiceId, path)
        print(f"Audio file received from ElevenLabs!")

        return path


    def deleteVoice(self, voice):
        print(f"Deleting {voice['name']}...")
        self.db.deleteVoice(voice['voice_id'])
        self.eLabs.deleteVoice(voice['voice_id'])
        shutil.rmtree(voice['path'])
        print(f"Successfully deleted {voice['name']}!")
        return
    
    
