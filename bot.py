#https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3267136&scope=bot
#https://discord.com/api/oauth2/authorize?client_id=1095890592753528872&permissions=3196928&scope=bot Dev

import os
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio
from dotenv import load_dotenv
from elevenLabs import ElevenLabs
import openai
from database import DataBase
from datetime import datetime, timedelta, timezone

footer_msg = "This bot was created by: JEFF#1778"
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',help_command=None,intents=intents)
bot.remove_command('help')
eLabs = ElevenLabs(os.getenv('ELEVENLABS_TOKEN'))
openai.api_key = os.getenv('OPENAI_TOKEN')



def makeErrorMessage(reason):
    embed = discord.Embed(title="Error",color=0xff0000)
    embed.add_field(name="Reason",value=reason)
    embed.set_footer(text=footer_msg)
    return embed

def checkUser(user):

    discordAccountDate = user.created_at

    now = datetime.now(timezone.utc)
    
    date_difference = now - discordAccountDate
    
    if date_difference < timedelta(days=30):
        return None

    foundUser = db.getUser(user)

    if foundUser is None:
        foundUser = db.addUser(user)

    return foundUser

#add a function to parse args

#different for members
@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Help",color=0x0000ff)
    embed.add_field(name="!speak",value="""Bot joins your channel and speaks the prompt output. 
                                            OpenAi language model 'gpt' is optional\n\n
                                            !speak <VoiceName> <gpt> | <Hello World!>\n\n
                                            Examples:\n
                                            >>   !speak JordanPeterson gpt | Tell me a story\n
                                            >>  !speak JordanPeterson | Say exactly this sentence""")

    embed.add_field(name="!add",value="""New Voice is added. Attached files will be used as samples for new voice\n\n
                                            Example:\n
                                            >>  !add JordanPeterson""")
    embed.set_footer(text=footer_msg)
    await ctx.send(embed=embed)
    return


@bot.command(name='speak')
async def speak(ctx):

    content = ctx.message.content

    voice = ctx.author.voice

    if voice is None:
        await ctx.send(embed=makeErrorMessage('You need to be in a voice channel to use this command.'))
        return

    channel = voice.channel

    user = checkUser(ctx.author)
    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return

    nextCharReset = datetime.fromtimestamp(eLabs.getCharCountResetDate())
    lastCharReset = user['last_char_reset']

    days_difference = nextCharReset - lastCharReset

    if days_difference > timedelta(days=30):
        db.resetMonthlyUserCharCount(user['user_id'])

        
    try:
        args = content.split("|")[0].strip()
        message = content.split("|")[1].strip()
    except IndexError:
        await ctx.send(embed=makeErrorMessage("Could not parse input. Use '!help' for assistance."))
        return

    argsList = args.split(" ")

    if len(argsList) > 2:
        gpt = argsList[2].strip() == "gpt"
    else:
        gpt = False

    voiceName = argsList[1].strip()

    if gpt:
        try:
            script = openai.Completion.create(model="text-davinci-003",prompt=message,temperature=0.7,max_tokens=200)["choices"][0]["text"]
        except:
            await ctx.send(embed=makeErrorMessage("Problem with openAi"))
            return
    else:
        script = message

    if(len(script) + user['monthly_chars_used'] > user['monthly_char_limit']):
        await ctx.send(embed=makeErrorMessage("You have reached your monthly character limit of " + str(user['monthly_char_limit']) + ".\n Your Characters will be reset on " + nextCharReset.strftime('%b %-d, %Y')))
        return

    voice = db.getVoice(user['user_id'],voiceName)

    if voice is None:
        await ctx.send(embed=makeErrorMessage("could not find voice '" + str(voiceName) + "' in database."))
        return

    prompt = db.addPrompt(args, user['user_id'], user['username'], message, script, len(script))
           
    outputPath = prompt['path']
    eLabs.textToSpeech(script, voice['voice_id'], outputPath)

    db.updateUserCharCount(user['user_id'], len(script))

    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
   
    try:
        voice_client: VoiceClient = await channel.connect()
    except asyncio.TimeoutError:
        return await ctx.send(embed=makeErrorMessage('Failed to connect to the voice channel. Please try again.'))

    audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=outputPath)

    if not voice_client.is_playing():
        voice_client.play(audio_source, after=lambda e: print('Finished playing', e))

        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()
    else:
        await ctx.send(embed=makeErrorMessage('I am already playing an audio file. Please wait until I finish.'))
    
    #add clickable emoji for replay?
    
#only for members
@bot.command(name='add')
async def add(ctx,*,content:str):
    user = checkUser(ctx.author)

    if not user:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new"))
        return
    
    files = ctx.message.attachments

    if len(files) == 0:
        await ctx.send(embed=makeErrorMessage("You need to attach files to add a new voice."))
        return

    voiceName = content.split(" ")[0].strip()

    try:
        accent = content.split(" ")[1].strip()
    except IndexError:
        accent = 'Canadian'

    try:
        isPrivate = content.split(" ")[2].strip() == 'private'
    except IndexError:
        isPrivate = False


    if isPrivate:
        path = f"voices/{user['user_id']}/{voiceName}"
    else:
        path = f"voices/public/{voiceName}"

    if not os.path.exists(path):
        os.makedirs(path)
    else:
        await ctx.send(embed=makeErrorMessage("The voice name already exists. Please choose another name."))
        return

    for file in files:
        if file.size >= 1000000:
            await ctx.send(embed=makeErrorMessage("Input file too large. All files must me under 10Mb"))
            return

        if file.content_type != 'audio/mpeg':
            await ctx.send(embed=makeErrorMessage("Input file must be an audio file"))
            return


        file_path = os.path.join(path, file.filename)
        await file.save(file_path)

    voice_id = eLabs.addVoice(path, voiceName, accent)

    db.addVoice(voice_id, voiceName, isPrivate, user['user_id'], path)

    embed = discord.Embed(title="Saved!", description=f"Voice '{voiceName}' saved successfully.", color=0x00ff00)
    embed.add_field(name="Command to play",value=f"!speak {voiceName} | your message")
    embed.set_footer(text=footer_msg)

    await ctx.send(embed=embed)


#new command !voices
#list available voices for that user
#/thisServer
#/public

#new command !list
#list users outputs

#add args 'prompt_id'
#can only download your own prompts
# @bot.command(name='download')
# async def download(ctx):
#     await ctx.send(file=discord.File("audioOutput/output.mp3"))

#new command !update 'voice'
#Add more samples to voice
#can only update voices you created

#new command !delete 'voice'
#delete voice 'voice'
#can only delete voices you created

#new command !chat
#just uses gpt4 (no voice cloning)

#new command !replay ouput
#play the selected output again

#new command !recents
#display recent command outputs
#use reactions to select which one to play?

#new command !usage
#display usage stats for that user
#display char limit, char count and refresh date

#new command !donate
#beg for money
#donate to add voices
#display my crypto wallet addresses

db = DataBase()
db.connect()
bot.run(TOKEN)