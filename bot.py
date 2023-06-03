#https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot
#https://discord.com/api/oauth2/authorize?client_id=1095890592753528872&permissions=3196928&scope=bot Dev
#TODO:

    #Voices to add
        #Purge  https://www.youtube.com/watch?v=BEkWdzd7ias
        #Joe Biden  https://www.youtube.com/watch?v=_J4IkbRh6W4&t=12s


        #David Goggins
        #Pierre Poilievre
        #Meg Griffin
        #Chris Griffin
        #Cleveland Brown
        #Quagmire
        #Joe Swanson
        #Lois Griffin
        #Stewie Griffin
        #Brian Griffin
        #Morty
        #Summer
        #Jerry
        #Beth
        
import os
import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import asyncio
from dotenv import load_dotenv
import openai
from dataManager import DataManager
from datetime import datetime, timedelta, timezone
import shutil
import random
from collections import namedtuple
import functools
import asyncio
import typing # For typehinting 


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!',help_command=None,intents=intents)
bot.remove_command('help')
openai.api_key = os.getenv('OPENAI_TOKEN')
dataManager = DataManager()
footer_msg = "This bot was created by: JEFF#1778"

def makeErrorMessage(reason):
    embed = discord.Embed(title="Error",color=0xff0000)
    embed.add_field(name="Reason",value=reason)
    embed.set_footer(text=footer_msg)
    return embed


def getUsageEmbed(user, username):
    embed = discord.Embed(title=username + "'s usage", color=0x0000ff, description="First Prompt: " + str(user['date_time'].strftime('%b %-d, %Y')))
    embed.add_field(name='Privilages',value=str(user['privileges']))
    embed.add_field(name="Total Characters Used", value=str(user['total_chars_used']))
    embed.add_field(name="Monthly Characters Used", value=str(user['monthly_chars_used']))
    embed.add_field(name="Monthly Character Limit", value=str(user['monthly_char_limit']))
    embed.add_field(name="Monthly Characters Remaining", value= str(user['monthly_char_limit'] - user['monthly_chars_used']))
    embed.add_field(name="Character Credit", value=user['char_credit'])
    embed.add_field(name="Next Character Reset", value=str((user['last_char_reset'] + timedelta(days=30)).strftime('%b %-d, %Y')))
    embed.set_footer(text=footer_msg)
    return embed


def getAboutEmbed():
    embed = discord.Embed(title="About Parrot",color=0x0000ff, description="""[Add Parrot to your server](https://discord.com/api/oauth2/authorize?client_id=1095014597871804510&permissions=3196992&scope=bot)\n
                                                                            [GitHub](https://github.com/Ferdinand737/voice-clone-bot)\n
                                                                            I built this bot using the [ElevenLabs](https://beta.elevenlabs.io/) and [OpenAi](https://platform.openai.com/) APIs. 
                                                                            Contact me <@273300302541881344> if you have any questions, suggestions or find any bugs.""")
    embed.add_field(name="Technologies Used", value="Implemented with python + discord library.\nMySql for data storage.\nHosted on my own server in the garage.\nIcon design by <@274019867764588544>.",inline=False)
    embed.set_footer(text=footer_msg)
    return embed


def getVoicesEmbed(serverId, serverName):
    thisServerVoices = dataManager.db.getServerVoices(serverId)
    publicVoices = dataManager.db.getPublicVoices()
    thisServerVoicesStr =''
    publicVoicesStr =''

    if thisServerVoices is not None:
        for voice in thisServerVoices:
            thisServerVoicesStr = thisServerVoicesStr + voice['name'] + " - " + voice['shortcut'] + "\n"
    else:
        thisServerVoicesStr = 'None'

    if publicVoices is not None:
        for voice in publicVoices:
            publicVoicesStr = publicVoicesStr + voice['name'] + " - " + voice['shortcut'] + "\n"
    else:
        publicVoicesStr = 'None'

    embed = discord.Embed(title="Available Voices", description="Each voice has a shortcut that can be used instead of the voice name.\nVoices and shortcuts are not case-sensetive.", color=0x0000ff)
    embed.add_field(name="Public", value=publicVoicesStr, inline=False)
    embed.add_field(name=f"In {serverName}", value=thisServerVoicesStr, inline=False)
    embed.set_footer(text=footer_msg)
    return embed


def getDonateEmbed():
    embed = discord.Embed(title="Donate",color=0x0000ff,description='API keys are not free, any donation helps.')
    
    embed.add_field(name='BTC', value="bc1qg944svjz7wydutldlzzfyxt04jaf5l3gvdquln", inline=False)
    embed.add_field(name='ETH', value='0x4C5B8E063A2b23926B9621619e90B5560B0F8AFc', inline=False)
    embed.add_field(name='XMR', value='48fMCSTJqZxFNY5RSwkfoa1GsffjxzZu6Wnk2x49VxKd3UGaaHWd86jTte6fWrtS7m2y6mTFKCCRMBxAVU51zNceAADkLpZ', inline=False)

    embed.set_footer(text=footer_msg)
    return embed

def parseArgs(command):

    currentCommand = command.split(" ")[0]

    if currentCommand == '!speak':

        options = {'voiceName':None, 'gpt':None, 'prompt':None}

        try:
            options['prompt'] = command.split("|")[1]
        except:
            print(f"Could not find prompt in command '{currentCommand}'.")
            return None

        arguments = command.split("|")[0].split(" ")

        arguments = [arg.strip() for arg in arguments]

        try:     
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'gpt' in arguments:
            options['gpt'] = 'gpt'

        return options
    
    if currentCommand == '!add':
        
        options = {'voiceName':None,'accent':None,'public':None}

        accents = ['american', 'british', 'african', 'australian','indian']

        arguments = [arg.strip() for arg in command.split(" ")]

        try:
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'public' in arguments:
            options['public'] = 'public'

        try:
            inputAccent = arguments[2]
            if inputAccent not in accents:
                print(f"Invalid accent '{inputAccent}' selected.")
            else:
                options['accent'] = inputAccent.capitalize()
        except:
            print(f"Could not find accent in command '{currentCommand}'.")

        return options
    
    if currentCommand == '!delete':

        options = {'voiceName':None,'public':None}

        arguments = [arg.strip() for arg in command.split(" ")]

        try:     
            options['voiceName'] = arguments[1]
        except:
            print(f"Could not find voice name in command '{currentCommand}'.")

        arguments = [arg.lower() for arg in arguments]

        if 'public' in arguments:
            options['public'] = 'public'

        return options
    
    if currentCommand == '!replay' or currentCommand == '!download':

        options = {'serverName': None}

        words = command.split()

        if len(words) >= 2:
            options['serverName'] = ' '.join(words[1:])

        return options


def checkUser(user):

    discordAccountDate = user.created_at

    now = datetime.now(timezone.utc)
    
    date_difference = now - discordAccountDate
    
    if date_difference < timedelta(days=30):
        return None

    foundUser = dataManager.db.getUser(user)

    if foundUser is None:
        foundUser = dataManager.db.addUser(user)

    return foundUser


def startCommand(ctx):
    
    serverId = ctx.guild.id
    serverName = ctx.guild.name
    username = f"{ctx.author.name}#{ctx.author.discriminator}"

    print(f"\nCommand '{ctx.message.content}' requested by {username} in {serverName}.")

    foundServer = dataManager.db.getServer(serverId)

    if foundServer is None:
        dataManager.db.addServer(serverId,serverName)


    user = checkUser(ctx.author)
    if user is None:
        return None

    return user, serverId, serverName


async def playAudio(ctx, channel, source):

    try:
        voice_client = await channel.connect()
    except:
        return await ctx.send(embed=makeErrorMessage('Failed to connect to the voice channel. Please try again.'))

    audio_source = discord.FFmpegPCMAudio(executable="ffmpeg", source=source)

    if not voice_client.is_playing():
        voice_client.play(audio_source)

        while voice_client.is_playing():
            await asyncio.sleep(1)
        await voice_client.disconnect()
    else:
        await ctx.send(embed=makeErrorMessage('I am already playing an audio file. Please wait until I finish.'))


async def run_blocking(blocking_func: typing.Callable, *args, **kwargs) -> typing.Any:
    """Runs a blocking function in a non-blocking way"""
    func = functools.partial(blocking_func, *args, **kwargs) # `run_in_executor` doesn't support kwargs, `functools.partial` does
    return await bot.loop.run_in_executor(None, func)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="!help"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f"Command not found: {ctx.message.content}")
        await help(ctx)
    else:
        print(error)


@bot.command(name='help')
async def help(ctx):

    user,serverId,serverName = startCommand(ctx)

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return


    commands = ['!speak','!add','!download','!replay','!voices','!delete','!usage','!donate','!about']

    def getHelpEmbed(title, description, example):
        toReturn = discord.Embed(title=title, color=0x0000ff, description=description)
        toReturn.add_field(name="Examples", value=example)
        return toReturn

    helpList = []

    helpList.append(getHelpEmbed('!speak',"""Parrot joins voice your channel and speaks prompt. 
                                 Use 'gpt' to use your input as a [ChatGPT](https://chat.openai.com) prompt.
                                 Each voice has a shortcut that can be used instead of the voice name.
                                 Voices and shortcuts are not case-sensetive.""",
                                 """!speak JordanPeterson | say exactly this
                                    !speak JordanPeterson gpt | tell me a story 
                                    !speak jp | say exactly this"""))
    
    helpList.append(getHelpEmbed('!add', 'Add a voice to your server by uploading file(s).\nAccent required.\nNo spaces allowed in voice name.', "!add JeffKaplan American"))

    helpList.append(getHelpEmbed('!download', 'View list of recent promts, click reactions to download.', """!download 
                                                                                                            !download serverName 
                                                                                                            !download all """))
    
    helpList.append(getHelpEmbed('!replay', 'View list of recent promts, click reactions to replay.', """!replay 
                                                                                                            !replay serverName 
                                                                                                            !replay all """))
    helpList.append(getVoicesEmbed(serverId, serverName))
    helpList.append(getHelpEmbed('!delete', 'Delete a voice that you added to your server.',"!delete BenShapiro\n!delete bs"))
    helpList.append(getUsageEmbed(user,ctx.author.display_name))
    helpList.append(getDonateEmbed())
    helpList.append(getAboutEmbed())
   
    embed = discord.Embed(title="Help",color=0x0000ff, description="Available Commands")
    for i, command in enumerate(commands):
        embed.add_field(name=command,value=f"{i+1}\u20e3")
    
    embed.set_footer(text=footer_msg)


    msg = await ctx.send(embed=embed)

    for i in range(len(commands)):
        await msg.add_reaction(f"{i+1}\u20e3")

   
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(helpList))]

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Timed out. Please try again.")
    else:
        index = [f"{i+1}\u20e3" for i in range(len(helpList))].index(str(reaction.emoji)) 
        await ctx.send(embed=helpList[index])
        return


@bot.command(name='speak')
async def speak(ctx):
    user,serverId,servername = startCommand(ctx)

    args = parseArgs(ctx.message.content)

    serverId = ctx.guild.id

    if args is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse input. Use !help for assistance.'))
        return

    if args['prompt'] is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse prompt. Use !help for assistance.'))
        return

    voice = ctx.author.voice

    if voice is None:
        await ctx.send(embed=makeErrorMessage('You need to be in a voice channel to use this command.'))
        return

    #channel = ctx.author.voice.channel
    channel = voice.channel

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return

    lastCharReset = user['last_char_reset']

    nextCharReset = lastCharReset + timedelta(days=30)

    days_difference = datetime.now() - lastCharReset

    if days_difference > timedelta(days=30):
        dataManager.db.resetMonthlyUserCharCount(user['user_id'])

    if ctx.voice_client:
        await ctx.voice_client.disconnect()
   
    clonedVoice = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

    if clonedVoice is None:
        await ctx.send(embed=makeErrorMessage(f"Could not find voice '{args['voiceName']}'."))
        return

    await ctx.send("Generating audio...")

    if args['gpt']:
        try:
            openaiInput = args['prompt'] + " Do not cut off mid sentence."
            print(f"Requesting response from OpenAi for prompt ({args['prompt']})...")
            script = openai.Completion.create(model="text-davinci-003",prompt=openaiInput,temperature=0.7,max_tokens=150)["choices"][0]["text"]
            print(f"Received response from OpenAi!")
        except:
            await ctx.send(embed=makeErrorMessage("Problem with openAi"))
            return
    else:
        script = args['prompt']

    availableMonthlyChars = user['monthly_char_limit'] - user['monthly_chars_used']
    availableCharCredit = user['char_credit']
    availableCharTotal = availableMonthlyChars + availableCharCredit

    if len(script) > availableCharTotal:
        await channel.disconnect()
        await ctx.send(embed=makeErrorMessage(f"This response would exceed your available characters ({availableCharTotal}).\n {user['monthly_char_limit']} characters will be added on {nextCharReset.strftime('%b %-d, %Y')}."))
        return
    
    outputPath = await run_blocking(dataManager.textToSpeech,args, clonedVoice['voice_id'], user['user_id'], serverId, script)

    if len(script) > availableMonthlyChars:
        dataManager.db.updateUserMonthlyCharCount(user['user_id'], user['monthly_char_limit'])
        remainingChars = len(script) - availableMonthlyChars
        dataManager.db.updateUserCreditCount(user['user_id'], availableCharCredit-remainingChars)
    else:
        dataManager.db.updateUserMonthlyCharCount(user['user_id'], user['monthly_chars_used'] + len(script))

    dataManager.db.updateUserTotalCharCount(user['user_id'], user['total_chars_used'] + len(script))

    await playAudio(ctx, channel, outputPath)
    
    
@bot.command(name='add')
async def add(ctx):
    user,serverId,servername  = startCommand(ctx)

    args = parseArgs(ctx.message.content)
    
    if args is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse input. Use !help for assistance.'))
        return

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return
    
    # if user['privileges'] == 'normal_user':
    #     await ctx.send(embed=makeErrorMessage("Only members can add voices to their server."))
    #     return
    
    if args['voiceName'] is None:
        await ctx.send(embed=makeErrorMessage('Unable to parse voice name. Use !help for assistance.'))
        return

    if args['public']:
        if user['privileges'] != 'admin':
            await ctx.send(embed=makeErrorMessage("Only admins can add public voices."))
            return
        serverId = None


    if args['accent'] is None:
        await ctx.send(embed=makeErrorMessage(f"""Invalid accent.
                                                Choose one of the following:\n
                                                -American
                                                -British
                                                -African
                                                -Australian
                                                -Indian
                                                \nTry:
                                                !add {args['voiceName']} American"""))
        return

    files = ctx.message.attachments

    if len(files) == 0:
        await ctx.send(embed=makeErrorMessage("You need to attach files to add a new voice."))
        return

    await ctx.send("Adding voice...")

    tempPath = f"temp/{random.randint(0, 2**32 - 1)}"

    clonedVoice = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

    if clonedVoice:
        await ctx.send(embed=makeErrorMessage("The voice name already exists. Please choose another name."))
        return

    if not os.path.exists(tempPath):
        os.makedirs(tempPath)

    for file in files:
        if file.size >= 10000000:
            await ctx.send(embed=makeErrorMessage(f"{file.filename} is too large. All files must me under 10Mb."))
            shutil.rmtree(tempPath)
            return
            
        allowedTypes = ['audio/aac', 'audio/x-aac', 'audio/x-aiff', 'audio/ogg', 'audio/mpeg', 'audio/mp3', 'audio/mpeg3', 
                        'audio/x-mpeg-3', 'audio/opus', 'audio/wav', 'audio/x-wav', 'audio/webm', 'audio/flac', 'audio/x-flac', 'audio/mp4']
        if file.content_type not in allowedTypes:
            await ctx.send(embed=makeErrorMessage("Input file must be an audio file"))
            shutil.rmtree(tempPath)
            return

       
        file_path = os.path.join(tempPath, file.filename)
        await file.save(file_path)

    newVoice = dataManager.addVoice(args['voiceName'], args['accent'], serverId, user['user_id'], tempPath)


    embed = discord.Embed(title="Saved!", description=f"Voice '{args['voiceName']}' saved successfully.", color=0x00ff00)
    embed.add_field(name="Commands to play",value=f"""!speak {args['voiceName']} | your message
                                                        !speak {newVoice['shortcut']} | your message
                                                        !speak {args['voiceName']} gpt | your prompt""")
    embed.set_footer(text=footer_msg)

    await ctx.send(embed=embed)


@bot.command(name='voices')
async def add(ctx):
    user,serverId,serverName = startCommand(ctx)
    await ctx.send(embed=getVoicesEmbed(serverId, serverName))


Result = namedtuple('Result', ['paths', 'check'])

async def replayAndDownloadHelper(ctx):
    user,serverId,servername  = startCommand(ctx)

    args = parseArgs(ctx.message.content)

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new"))
        return
    
    if args['serverName'] is None:
        prompts = dataManager.db.getServerPrompts(user['user_id'], serverId, 9)
        where = servername
    
    elif args['serverName'] != 'all':
        server = dataManager.db.getServerByName(args['serverName'])

        if server is None:
            await ctx.send(embed=makeErrorMessage(f"Could not find server '{args['serverName']}'."))
            return

        prompts = dataManager.db.getServerPrompts(user['user_id'], server['server_id'], 9)

        where = server['server_name']

    else:
        prompts = dataManager.db.getUserPrompts(user['user_id'], 9)
        where = 'all servers'

    if prompts is None:
        await ctx.send(embed=makeErrorMessage("No prompts found"))
        return
    
    paths = []
    embed = discord.Embed(title=f"Your recent prompts in {where}.",description="React to replay.", color=0x0000ff)
    for i, prompt in enumerate(prompts):
        try:
            paths.append(prompt['path'])
            embed.add_field(name=f"{i+1}\u20e3  {prompt['command']}",value=f">  {prompt['prompt'][:40]}...",inline=False)
        except FileNotFoundError:
            pass
    
    if len(paths) == 0:
        await ctx.send(embed=makeErrorMessage("No prompts found"))
        return
   
    embed.set_footer(text=footer_msg)
    msg = await ctx.send(embed=embed)

    for i in range(len(paths)):
        await msg.add_reaction(f"{i+1}\u20e3")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in [f"{i+1}\u20e3" for i in range(len(paths))]


    return Result(paths=paths, check=check)

@bot.command(name='download')
async def download(ctx):
   
    result = await replayAndDownloadHelper(ctx)
    paths = result.paths

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=result.check)
    except asyncio.TimeoutError:
        pass
    else:
        index = [f"{i+1}\u20e3" for i in range(len(paths))].index(str(reaction.emoji)) 
        await ctx.send(file=discord.File(paths[index]))
        await ctx.send("File sent.")


@bot.command(name='replay')
async def replay(ctx):

    result = await replayAndDownloadHelper(ctx)
    paths = result.paths

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=result.check)
    except asyncio.TimeoutError:
        pass
    else:
        index = [f"{i+1}\u20e3" for i in range(len(paths))].index(str(reaction.emoji)) 

        voice = ctx.author.voice

        if voice is None:
            await ctx.send(embed=makeErrorMessage('You need to be in a voice channel to use this command.'))
            return

        channel = voice.channel

        await playAudio(ctx, channel, paths[index])
        

@bot.command(name='delete')
async def delete(ctx):
    user,serverId,serverName = startCommand(ctx)

    args = parseArgs(ctx.message.content)

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new"))
        return

    # if user['privileges'] == 'normal_user':
    #     await ctx.send(embed=makeErrorMessage("Only members can delete voices."))
    #     return

    if args['public'] and user['privileges'] != 'admin':
        await ctx.send(embed=makeErrorMessage("Only admins can delete public voices"))
        return
     

    if user['privileges'] == 'admin':

        if args['public']:

            voiceToDelete = await run_blocking(dataManager.getVoice, None, args['voiceName'])

            if voiceToDelete is None:
                await ctx.send(embed=makeErrorMessage(f"Could not find {args['voiceName']}."))
                return
        else:

            voiceToDelete = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

            if voiceToDelete is None:
                await ctx.send(embed=makeErrorMessage(f"Could not find {args['voiceName']} in {serverName}"))
                return

    else:

        voiceToDelete = await run_blocking(dataManager.getVoice, serverId, args['voiceName'])

        if voiceToDelete is None:
            await ctx.send(embed=makeErrorMessage(f"Could not find {args['voiceName']}."))
            return

        if voiceToDelete['user_id'] != user['user_id']:
            await ctx.send(embed=makeErrorMessage("You can only delete voices that you added."))
            return

    dataManager.deleteVoice(voiceToDelete)
   
    embed = discord.Embed(title="Deleted!", description=f"Voice '{voiceToDelete['name']}' deleted successfully.", color=0x00ff00)
    embed.set_footer(text=footer_msg)
    await ctx.send(embed=embed)


@bot.command(name='usage')
async def usage(ctx):
    user,serverId,servername = startCommand(ctx)

    if user is None:
        await ctx.send(embed=makeErrorMessage("Your discord account is too new."))
        return
    await ctx.send(embed=getUsageEmbed(user,ctx.author.display_name))


@bot.command(name='about')
async def about(ctx):
    startCommand(ctx)
    await ctx.send(embed=getAboutEmbed())


@bot.command(name='donate')
async def donate(ctx):
    startCommand(ctx)
    await ctx.send(embed=getDonateEmbed())



bot.run(TOKEN)