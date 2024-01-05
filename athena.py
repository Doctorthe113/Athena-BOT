# built-in libraries
import io
import os
import json
import re
import threading
import random
# external libraries and apis
import nextcord
import psutil
import requests
import yt_dlp

from nextcord import Interaction
from nextcord.ext import tasks
from googletrans import Translator, LANGUAGES
from ytmusicapi import YTMusic
from dotenv import load_dotenv
from datetime import datetime

from phrases import phrase
from extentions.web_search import webSearch
from extentions.desco import descoAPI

load_dotenv()

# loading global variables
TOKEN = os.getenv(key="TOKEN")
API_KEY = os.getenv(key="googleApiKey")
CSE_ID = os.getenv(key="searchEngineId")
EMOJI_REGEX = re.compile(pattern=(r"<:(\w+):(\d+)>"))
URL_REGEX = re.compile(
    pattern=r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*")
PUNC_REGEX = re.compile(pattern=r"[^\w\s.:]")
LOG_CHANNEL = None
FFMPEG_OPTIONS = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
vcs = {}
queue = {}

# loading differebnt classes and etcs
intents = nextcord.Intents.default()
intents.message_content = True
client = nextcord.Client(intents=intents)

translator = Translator()
phraseObj = phrase()
webSearchObj = webSearch(apiKey=API_KEY, cseId=CSE_ID)

ytdlMusic = yt_dlp.YoutubeDL({"format": "bestaudio"})


@client.event
async def on_ready():
    loginTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    global LOG_CHANNEL
    LOG_CHANNEL = await client.fetch_channel(1115589968929239153)

    print(f"{loginTime}: Logged in as {client.user}")
    thread = threading.active_count()
    print(f"Current active thread count: {thread}")


@client.event
async def on_message(rawMsg):
    with open("guild.json", "r") as foo:
        guilds = json.load(foo)
    translateGuilds = guilds["translate"]
    dadJokeGuilds = guilds["dadPrompts"]
    uwuGuilds = guilds["uwuPrompts"]

    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msgChannelId = rawMsg.channel.id
    randomChance = random.randint(1, 3)

    # filtering messages for future
    filteredMsgNoEmoji = re.sub(EMOJI_REGEX, "", rawMsg.content)
    filteredMsgNoURL = re.sub(URL_REGEX, "", filteredMsgNoEmoji)
    filteredMsg = re.sub(PUNC_REGEX, "", filteredMsgNoURL)
    filteredMsgLow = filteredMsg.lower()


    # music queue function
    async def queue_check(error=None):
        try:
            if len(queue[vc.guild.id][0]) > 0:
                queueSong = queue[vc.guild.id][0][0]
                queueMusic = nextcord.FFmpegPCMAudio(
                    queueSong, **FFMPEG_OPTIONS)
                queue[vc.guild.id][0].pop(0)
                queue[vc.guild.id][1].pop(0)
                await vc.play(queueMusic, after=queue_check)
            else:
                await vc.disconnect()
                del queue[vc.guild.id]
        except:   
                print(f"An error has occured. {e}")
                await vc.disconnect()
                del queue[vc.guild.id]


    # skips if message author is bot itself
    if rawMsg.author == client.user:
        return None

    # skips if message content is none
    if filteredMsg == "" or filteredMsg == None:
        return None

    # logging messages
    if rawMsg.channel != LOG_CHANNEL:
        await LOG_CHANNEL.send(f"{currentTime}: {rawMsg.author.name} -> {rawMsg.content}")

    # *For non-prompt/automated responses
    # translating messages
    if msgChannelId in translateGuilds:
        if (translator.detect(filteredMsgLow).lang != "en" and
                not set(filteredMsgLow.split()).intersection(phraseObj.UWUPROMPT)):
            translateMsg = translator.translate(filteredMsgNoEmoji)
            translateMsgSrc = LANGUAGES.get(translateMsg.src)
            await rawMsg.reply(f"*From {translateMsgSrc}* \n>>> {translateMsg.text}",
                               mention_author=False)

    # saying hi/hello
    if filteredMsgLow.startswith(phraseObj.GREETINGPROMPT):
        greet = phraseObj.greetingMethod()
        await rawMsg.channel.send(greet)

    # magic 8 ball
    if filteredMsgLow.startswith(phraseObj.MAGIC8BALLPROMPT):
        bar = phraseObj.magic8ballMethod()
        await rawMsg.reply(bar)
        return None

    # rolling a dice
    if filteredMsgLow == "roll a dice":
        dice = phraseObj.rollDiceMethod()
        await rawMsg.reply(f"🎲 {dice} 🎲")
        return None

    # ping test
    if filteredMsgLow == "ping":
        await rawMsg.reply(f"Pong! Bot Latency `{round(client.latency * 1000)}ms`")
        return None

    # dad joke ("hi x, im dad" type)
    if msgChannelId not in dadJokeGuilds:
        for i in phraseObj.DADPROMPT:
            if randomChance == 2 and filteredMsgLow.startswith(i):
                bar = filteredMsgLow.partition(i)[-1]
                await rawMsg.reply(f"Hi, {bar}, I am Athena!", mention_author=False)

    # uwu roasts
    if msgChannelId not in uwuGuilds:
        for i in phraseObj.UWUPROMPT:
            if randomChance == 2 and i in filteredMsgLow:
                bar = phraseObj.uwuRoastMethod()
                await rawMsg.reply(bar)


# *Prompt based non-slash commands
    for prompt in phraseObj.PROMPT:
        # for skipping iterations
        if prompt not in filteredMsgLow:
            continue

        # telling dad jokes
        if (filteredMsgLow.startswith(f"{prompt}tell me a joke") or
                filteredMsgLow.startswith(f"{prompt}tell me a dad joke")):
            await rawMsg.reply(phraseObj.dadJokeMethod())
            break

        # checking system
        if filteredMsgLow.startswith(f"{prompt}check system"):
            thread = threading.active_count()
            process = psutil.Process(os.getpid())
            memoryUsage = process.memory_info().rss / 1048576
            await rawMsg.reply(f"Thread: {thread}, Memory: {memoryUsage} MB")
            break

        # json validator
        if filteredMsgLow.startswith(f"{prompt}validate this json"):
            jsonForCheck = re.sub(r"^```json\n|```$", "", rawMsg.content)
            try:
                baz = json.loads(jsonForCheck)
                await rawMsg.reply("This json is valid.", mention_author=False)
            except ValueError as e:
                await rawMsg.reply(f"This json isn't valid. ```{e}```")
                break

        # google search
        if filteredMsgLow.startswith(f"{prompt}what is"):
            query = re.sub(f"{prompt}what is", "",
                           rawMsg.content, flags=re.IGNORECASE)
            result = webSearchObj.google_search(query)
            await rawMsg.reply(result)
            break

        if (filteredMsgLow.startswith(f"{prompt}search for") and
                filteredMsgLow.endswith("on google")):
            query = re.sub(f"^{prompt}search for | on google$", "", rawMsg.content,
                           flags=re.IGNORECASE)
            result = webSearchObj.google_search(query)
            await rawMsg.reply(result)
            break

        # wikipedia search
        if (filteredMsgLow.startswith(f"{prompt}search for") and
                filteredMsgLow.endswith("on wikipedia")):
            query = re.sub(f"^{prompt}search for | on wikipedia$", "", filteredMsg,
                           flags=re.IGNORECASE)
            wikiSummary = webSearchObj.wikiSearch(query)[0]
            relatedArticles = webSearchObj.wikiSearch(query)[1]
            relatedArticles = chr(10).join(relatedArticles)
            await rawMsg.reply(f"**__Related titles:__** \n```{relatedArticles}  ```",
                               mention_author=False)
            await rawMsg.reply(f"**__Summary of your query__**: \n```{wikiSummary} ```")
            break

        # purging messages
        if (filteredMsgLow.startswith(f"{prompt}purge") and
                rawMsg.author.guild_permissions.manage_messages):
            numOfMsg = re.sub(f"{prompt}purge", "", filteredMsgLow)
            await rawMsg.channel.send(f"{numOfMsg} messages purged.")
            await rawMsg.channel.purge(limit=int(numOfMsg) + 2)
            break

        # defining words
        if filteredMsgLow.startswith(f"{prompt}define"):
            query = re.sub(f"{prompt}define", "", filteredMsg)
            result = webSearchObj.dictionary(query)
            await rawMsg.reply(f"### {result[0]} \n" +
                               f"### {result[1]} \n" +
                               f"__Pronounciation__: {result[2]} \n" +
                               f"__Origin__: {result[3]} \n" +
                               f"__Definitions__:{result[4]}")
            break

        # !Needs to refactored because it's way too ugly  
        # for playing music
        if filteredMsgLow.startswith(f"{prompt}play"):
            url = re.sub(f"{prompt}play", "",
                         rawMsg.content, flags=re.IGNORECASE)
            try:
                vc = await rawMsg.author.voice.channel.connect()
                vcs[vc.guild.id] = vc
                queue[rawMsg.guild.id] = [[], []]
            except nextcord.ClientException as e:
                await rawMsg.reply(f"Error joining the channel. {e}")
            try:
                data = ytdlMusic.extract_info(url, download=False)
                song = data["url"]
                title = data["title"]
                music = nextcord.FFmpegPCMAudio(song, **FFMPEG_OPTIONS)
                vc.play(music, after=queue_check)
                await rawMsg.reply(f"Now playing {title}")
                break
            except:
                pass
            try:
                musicId = YTMusic().search(url, "songs")[0]["videoId"]
                data = ytdlMusic.extract_info(musicId, download=False)
                song = data["url"]
                title = data["title"]
                music = nextcord.FFmpegPCMAudio(song, **FFMPEG_OPTIONS)
                vc.play(music, after=queue_check)
                await rawMsg.reply(f"Now playing {title}")
            except nextcord.ClientException as e:
                await rawMsg.reply(f"An error has occured. {e}")
            break

        # adding music to queue:
        if filteredMsgLow.startswith(f"{prompt}queue"):
            url = re.sub(f"{prompt}queue", "",
                         rawMsg.content, flags=re.IGNORECASE)
            try:
                data = ytdlMusic.extract_info(url, download=False)
            except:
                musicId = YTMusic().search(url, "songs")[0]["videoId"]
                data = ytdlMusic.extract_info(musicId, download=False)
            song = data["url"]
            title = data["title"]
            queue[rawMsg.guild.id][0].append(song)
            queue[rawMsg.guild.id][1].append(title)
            await rawMsg.reply(f"Added {title} to the queue")
            break

        # for pausing music
        if filteredMsgLow.startswith(f"{prompt}pause"):
            try:
                vcs[rawMsg.guild.id].pause()
            except nextcord.ClientException as e:
                await rawMsg.reply("An error has occured.")
            break

        # for skipping music
        if filteredMsgLow.startswith(f"{prompt}skip"):
            try:
                vcs[rawMsg.guild.id].pause()
                vc = vcs[rawMsg.guild.id]
                nextSong = queue[rawMsg.guild.id][0][0]
                nextMusic = nextcord.FFmpegPCMAudio(
                    nextSong, **FFMPEG_OPTIONS)
                await rawMsg.reply(f"Skipped to {queue[rawMsg.guild.id][1][0]}.")
                queue[rawMsg.guild.id][0].pop(0)
                queue[rawMsg.guild.id][1].pop(0)
                vc.play(nextMusic, after=queue_check)
            except:
                await rawMsg.reply("An error has occured.")
            break

        # for resuming music
        if filteredMsgLow.startswith(f"{prompt}resume"):
            try:
                vcs[rawMsg.guild.id].resume()
            except nextcord.ClientException as e:
                await rawMsg.reply("An error occured.")
            break

        # for disconnecting/stopping music
        if filteredMsgLow.startswith(f"{prompt}stop"):
            try:
                await vcs[rawMsg.guild.id].disconnect()
                del queue[rawMsg.guild.id]
            except:
                await rawMsg.reply("An error has occured.")
            break

        # for checking queue
        if filteredMsgLow.startswith(f"{prompt}check queue"):
            try:
                queueList = chr(10).join(queue[rawMsg.guild.id][1])
                await rawMsg.reply(f"```\n{queueList}```")
            except:
                await rawMsg.reply("Queue is empty.")

        # for downloading videos
        if filteredMsgLow.startswith(f"{prompt}download"):
            query = re.sub(f"{prompt}download", "",rawMsg.content, flags=re.IGNORECASE)
            ytdlVid = yt_dlp.YoutubeDL({"format": "best", "quiet": True})
            data = ytdlVid.extract_info(query, download=False)
            url = data["url"]
            await rawMsg.reply("Downloading...")
            try:
                response = requests.get(url, timeout=13, stream=True)
                content = response.content
                videoBinary = io.BytesIO(content)
                video = nextcord.File(videoBinary, filename="video.mp4")
                await rawMsg.channel.send(file=video)
            except:
                await rawMsg.channel.send("An error has occured.")

        # replying to mentions
        if filteredMsgLow == prompt:
            await rawMsg.reply("Hey that's me! 🙋‍♀️")
            break


# slash command for feedback:
@client.slash_command(name="feedback", description="Send feedback directly.")
async def feedback(interaction: Interaction, arg: str):
    FEEDBACKCHANNEL = await client.fetch_channel(1126220831496863786)
    userName = interaction.user.name
    try:
        await FEEDBACKCHANNEL.send(f"From {userName}, \n{arg}")
    except (nextcord.errors.ApplicationInvokeError, nextcord.errors.Forbidden,
            nextcord.errors.HTTPException) as e:
        await interaction.response.send_message(f"Feedback couldn't be sent. Error: \n" +
                                                f"```{e} ```")


# check my electric meter balance
@tasks.loop(hours=12)
async def desco_balance_checker():
    DOCId = await client.fetch_user(699342617095438479)
    for i in (12021574, 12021575):
        balance = descoAPI(i).balanceCheck()["balance"]
        monthlyUse = descoAPI(i).balanceCheck()["currentMonthConsumption"]
        if int(balance) <= 250:
            await DOCId.send(f"Heyy, {balance}৳ Balance left in {i}. \n" +
                             f"This month's consumption upto today is {monthlyUse}৳.")


desco_balance_checker.start()
client.run(TOKEN)
