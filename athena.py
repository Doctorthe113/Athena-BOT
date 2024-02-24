# author: @doctorthe113
# github: https://github.com/Doctorthe113/Athena-BOT
# version: 1.13.1

# __formatting style__: camel case for variables, snake case for functions, 
# UPPERCASE for constants. Extra indent for if statement.


# built-in libraries
import asyncio
import io
from itertools import cycle
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
from nextcord.ext import tasks, commands
from googletrans import Translator, LANGUAGES
from ytmusicapi import YTMusic
from dotenv import load_dotenv
from datetime import datetime

from extentions.phrases import Phrase
from extentions.web_search import WebSearch
from extentions.desco import DescoAPI
from extentions.queue_check import queue_check, queue_del, queue_grab, queue_loop, queue_make, queue_add
from extentions.nasa import Nasa

load_dotenv()



#* loading global variables
vcs = {} # {guild_id: voice_client_object}
logChannel = None
statuses = cycle([
        "hello bbg 😏", 
        "in your walls 👀", 
        "Doctor chan my beloved 😍", 
        "Yo Anna, where you at?"
    ])

TOKEN = os.getenv(key="TOKEN")
GOOGLE_API = os.getenv(key="googleAPI")
CSE_ID = os.getenv(key="searchEngineId")
NASA_API = os.getenv(key="nasaAPI")
NINJA_API = os.getenv(key="ninjaAPI")
EMOJI_REGEX = re.compile(pattern=(r"<:(\w+):(\d+)>"))
URL_REGEX = re.compile(
    pattern=r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
PUNC_REGEX = re.compile(r"(?<!\A)[^\w\s]")
FFMPEG_OPTIONS = {
    "options": "-vn",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}



#* loading differebnt classes and etcs
translator = Translator()
phraseObj = Phrase()
webSearchObj = WebSearch(apiKey=GOOGLE_API, cseId=CSE_ID)
nasaObj = Nasa(apiKey=NASA_API)
ytdlMusic = yt_dlp.YoutubeDL({"format": "bestaudio"})

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(
    command_prefix=phraseObj.PREFIX, 
    intents=intents
)
bot.remove_command('help')



@bot.event
async def on_ready():
    loginTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    global logChannel
    logChannel = await bot.fetch_channel(1115589968929239153)

    print(f"{loginTime}: Logged in as {bot.user}")
    thread = threading.active_count()
    print(f"Current active thread count: {thread}")

@bot.event
async def on_message(rawMsg):
    with open("guild.json", "r") as foo:
        guilds = json.load(foo)
    translateGuilds = guilds["translate"]
    dadJokeGuilds = guilds["dadPrompts"]
    uwuGuilds = guilds["uwuPrompts"]

    currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msgChannelId = rawMsg.channel.id
    randomChance = random.randint(1, 10)

    # filtering messages for future
    filteredMsg = re.sub(EMOJI_REGEX, "", rawMsg.content)
    filteredMsg = re.sub(URL_REGEX, "", filteredMsg)
    filteredMsgPunc = re.sub(PUNC_REGEX, "", filteredMsg)
    filteredMsgLow = filteredMsgPunc.lower()

    # skips if message author is bot itself
    if rawMsg.author == bot.user:
        return None

    # skips if message content is none
    if filteredMsg == None:
        return None

    # logging messages
    if rawMsg.channel != logChannel:
        await logChannel.send(
            f"{currentTime}: {rawMsg.author.name} -> {rawMsg.content}"
        )

    # *For non-prompt/automated responses
    # translating messages
    if msgChannelId in translateGuilds:
        filteredMsgLowSet = set(filteredMsgLow.split())
        if (translator.detect(filteredMsg).lang != "en" 
                and not filteredMsgLowSet.intersection(phraseObj.UWUPROMPT)
                and not filteredMsgLow.startswith(phraseObj.PREFIX)
            ):
            translation = translator.translate(filteredMsg)
            translationSrc = LANGUAGES.get(translation.src)
            msg = await rawMsg.reply(
                f"*__From {translationSrc}__*\n>>> {translation.text}",
                mention_author=False
            )
            await msg.add_reaction("❌")
            if randomChance == 2:
                await msg.reply(
                    "(*React with ❌ to delete wrong translations*)",
                    mention_author=False
                )

            def check(reaction, user):
                return (
                    user == rawMsg.author
                    and str(reaction.emoji) == "❌"
                    and reaction.message.id == msg.id
                )

            try:
                reaction, user = await bot.wait_for(
                    "reaction_add", 
                    timeout=60.0, 
                    check=check
                )
                await msg.delete()
            except nextcord.errors.Forbidden as e:
                await msg.channel.send(f"Error deleting the message: {e}")
            except asyncio.TimeoutError:
                pass

    # saying hi/hello
    if filteredMsgLow == phraseObj.GREETINGPROMPT:
        greet = phraseObj.greeting_method()
        await rawMsg.channel.send(greet)

    # magic 8 ball
    if filteredMsgLow.startswith(phraseObj.MAGIC8BALLPROMPT):
        bar = phraseObj.magic8ball_method()
        await rawMsg.reply(bar)
        return None

    # rolling a dice
    if filteredMsgLow == "roll a dice":
        dice = phraseObj.roll_dice_method()
        await rawMsg.reply(f"🎲 {dice} 🎲")
        return None

    # ping test
    if filteredMsgLow == "ping":
        await rawMsg.reply(f"Pong! Bot Latency `{round(bot.latency * 1000)}ms`")
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
                bar = phraseObj.uwu_roast_method()
                await rawMsg.reply(bar)

    # for mentions
    for prompt in phraseObj.PREFIX:
        if filteredMsgLow == prompt:
            await rawMsg.reply("Hey that's me! 🙋‍♀️")
            break

    await bot.process_commands(rawMsg)



#* For commands
# for pinging the bot. eg: "ping"
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! Bot Latency `{round(bot.latency * 1000)}ms`")

# for help. eg: "help"
@bot.command()
async def help(ctx):
    helpMsg = phraseObj.helpMsg
    await ctx.send(helpMsg)
    pass

# for a dad joke. eg:"tell me a joke"
@bot.command()
async def tell(ctx, *, arg):
    if not arg.startswith(("me a joke", "me a dad joke")):
        return None
    await ctx.send(phraseObj.dad_joke_method())

# for bored. eg: "i am bored"
@bot.command(aliases = ["I"])
async def i(ctx, *, arg):
    if not arg.startswith("am bored"):
        return None
    await ctx.send(f"Here's an activity for you: {phraseObj.bored()}")

# for checking resources. eg: "check resources"
@bot.command()
async def check(ctx, *, arg):
    if not arg.startswith("resources"):
        return None
    thread = threading.active_count()
    process = psutil.Process(os.getpid())
    memoryUsage = process.memory_info().rss / 1048576
    await ctx.send(f"Thread: {thread}, Memory: {memoryUsage} MB")

# for googling results. eg: "what is x"
@bot.command()
async def what(ctx, *, arg):
    if not arg.startswith("is"):
        return None
    query = re.sub("what is", "", arg, flags=re.IGNORECASE)
    result = webSearchObj.google_search(query)
    await ctx.send(result)

# for googling results. eg: "google x"
@bot.command()
async def google(ctx, *, arg):
    result = webSearchObj.google_search(arg)
    await ctx.send(result)

# for searching wikipedia. eg: "search x on wikipedia"
@bot.command()
async def search(ctx, *, arg):
    if not (arg.startswith("for") 
            and arg.endswith(" on wikipedia")):
        return None
    query = re.sub("^for | on wikipedia$", "", arg, flags=re.IGNORECASE)
    wikiSummary = webSearchObj.wikiSearch(query)[0]
    relatedArticles = webSearchObj.wikiSearch(query)[1]
    relatedArticles = "\n".join(relatedArticles)
    msg = await ctx.reply(f"**__Summary of your query__**: ```\n{wikiSummary}```")
    await msg.reply(f"**__Related articles__**: ```\n{relatedArticles}```")

# for deleting messages. eg: "purge n"
@bot.command()
async def purge(ctx, *, arg):
    if not (ctx.author.guild_permissions.manage_messages):
        return None
    msgCount = arg
    await ctx.send(f"Purging {msgCount} messages...")
    await ctx.channel.purge(limit=int(msgCount) + 2)

# for defining words. eg: "define x"
@bot.command()
async def define(ctx, *, arg):
    try:
        result = webSearchObj.dictionary(arg)
        await ctx.send(
                f"### {result[0]} \n"
                + f"### {result[1]} \n"
                + f"__Pronounciation__: {result[2]} \n"
                + f"__Origin__: {result[3]} \n"
                + f"__Definitions__:{result[4]}"
            )
    except:
        await ctx.send("An error has occured.")

# for downloading videos. eg: "download https://www.youtube.com/watch?v=x"
@bot.command()
async def download(ctx, arg):
    ytdlVid = yt_dlp.YoutubeDL({"format": "best", "outtml": "-", "quiet": True})
    data = ytdlVid.extract_info(arg, download=False)
    url = data["url"]
    msg = await ctx.send("Downloading...")
    try:
        response = requests.get(url, timeout=13, stream=True)
        contentBinary = response.content
        binaryFileObj = io.BytesIO(contentBinary)
        video = nextcord.File(binaryFileObj, filename="video.mp4")
        await msg.reply(file=video)
    except (
        nextcord.errors.HTTPException,
        nextcord.errors.Forbidden,
        requests.exceptions.Timeout,
        requests.exceptions.HTTPError,
    ) as e:
        await msg.reply(f"An error has occured. {e}")

# for starting music playback. eg: "join"
@bot.command()
async def join(ctx):
    try:
        vc = await ctx.author.voice.channel.connect()
        vcs[vc.guild.id] = vc
        dj = ctx.author.name
        queue_make(vc)
        await ctx.send(f"Joined {dj}'s voice channel!")
    except AttributeError:
        await ctx.send("You haven't joined a voice channel yet, silly! 😒")

# for stopping music playback. eg: "stop"
@bot.command()
async def stop(ctx):
    vc = vcs[ctx.guild.id]
    try:
        await vc.disconnect()
        await ctx.send("Stopped the music playback, cya later! 😊")
        del vcs[ctx.guild.id]
    except:
        await ctx.send("I am unable to properly stop the music 😔")

# for adding music to the queue. eg: "add https://www.youtube.com/watch?v=x"
@bot.command()
async def add(ctx, *, arg):
    vc = vcs[ctx.guild.id]
    try:
        data = ytdlMusic.extract_info(arg, download=False)
    except:
        musicID = YTMusic().search(arg, "songs")[0]["videoId"]
        data = ytdlMusic.extract_info(musicID, download=False)
    songURL = data["url"]
    title = data["title"]
    queue_add(vc, songURL, title)
    await ctx.send(f"Added __{title}__ to the queue.")

# for starting/playing music. eg: "play"
@bot.command()
async def play(ctx):
    try:
        vc = vcs[ctx.guild.id]
    except:
        await ctx.send("I am not connected to a voice channel 😔")
        return None
    if not vc.is_playing():
        queue = queue_grab(vc)
        songURL = queue[0][0]
        track = nextcord.FFmpegPCMAudio(
                songURL,
                **FFMPEG_OPTIONS
            )
        vc.play(track, after=lambda e: queue_check(vc))
    else:
        await ctx.send("I am already playing! Use `athena add` to add music.")

# for pausing music. eg: "pause"
@bot.command()
async def pause(ctx):
    try:
        vc = vcs[ctx.guild.id]
        vc.pause()
        await ctx.send("Paused!")
    except:
        await ctx.send("I am not playing anything right now 😔")

# for resuming music. eg: "resume"
@bot.command()
async def resume(ctx):
    try:
        vc = vcs[ctx.guild.id]
        vc.resume()
        await ctx.send("Resumed!")
    except:
        await ctx.send("I have not anything paused right now 😀")

# for looping music. eg: "loop"
@bot.command()
async def loop(ctx):
    try:
        vc = vcs[ctx.guild.id]
        queue_loop(vc)
        await ctx.send("Looping the current queue!")
    except:
        await ctx.send("I am unable to loop 😔")

# for skipping music. eg: "skip"
@bot.command()
async def skip(ctx):
    try:
        vc = vcs[ctx.guild.id]
    except:
        await ctx.send("I am not connected to a voice channel 😔")
    if not vc.is_playing() or not vc:
        await ctx.send("I am not playing anything right now 😔")
    else:
        vc.pause()
        queue_check(vc)
        await ctx.send("Skipping!")

# for checking queue. eg: "queue"
@bot.command()
async def queue(ctx):
    try:
        vc = vcs[ctx.guild.id]
        queue = queue_grab(vc)
        queueList = "\n".join(queue[1])
        await ctx.send(f"```\n{queueList}```")
    except:
        await ctx.send("Queue is empty.")

# for NASA images. eg: "nasa"
@bot.command()
async def nasa(ctx):
    photoLink = nasaObj.getPhoto()
    try:
        await ctx.send(photoLink)
    except:
        await ctx.send("I am unable to send this beautiful image 😔")

# for finiding someone's age. eg: "agify John"
@bot.command()
async def agify(ctx, *, arg):
    age = phraseObj.agify(arg)
    if age < 18:
        await ctx.send(f"{arg} is {age} years old!")
    else:
        await ctx.send(f"{arg} is **{age}** years old! What a boomer!🥳")

# for random dog images. eg: "dog"
@bot.command()
async def dog(ctx):
    await ctx.send(phraseObj.dog())

# for random cat images. eg: "cat"
@bot.command()
async def cat(ctx):
    await ctx.send(phraseObj.cat())

# for random cocktail. eg: "cocktail random/{cocktail name}"
@bot.command()
async def cocktail(ctx, *, arg):
    if arg.lower() == "random":
        await ctx.send(phraseObj.random_cocktail())
    else:
        await ctx.send(phraseObj.search_cocktail(arg))

# for random facts. eg: "fact"
@bot.command()
async def fact(ctx):
    await ctx.send(phraseObj.fact(NINJA_API))

# for random bucketlist. eg: "bucketlist"
@bot.command()
async def bucket(ctx, *, arg):
    if not arg == "list":
        return None
    await ctx.send(phraseObj.bucket_list(NINJA_API))

# for finiding rhyming words. eg: "rhyme"
@bot.command()
async def rhyme(ctx, *, arg):
    words = phraseObj.rhyme(NINJA_API, arg)
    await ctx.send(f"__**Here are few words that rhyme with {arg}:**__```\n{words}```")



#* Slash Commands
# slash command for feedback:
@bot.slash_command(name="feedback", description="Send feedback directly.")
async def feedback(interaction: Interaction, arg: str):
    FEEDBACKCHANNEL = await bot.fetch_channel(1126220831496863786)
    userName = interaction.user.name
    try:
        await FEEDBACKCHANNEL.send(f"From {userName}, \n{arg}")
        await interaction.response.send_message("Feedback sent!", ephemeral=True)
    except (
        nextcord.errors.ApplicationInvokeError,
        nextcord.errors.Forbidden,
        nextcord.errors.HTTPException,
    ) as e:
        await interaction.response.send_message(
            "Feedback couldn't be sent. Error: \n" + f"```{e} ```"
        )



# check my electric meter balance
@tasks.loop(hours=12)
async def desco_balance_checker():
    docID = await bot.fetch_user(699342617095438479)
    for i in (12021574, 12021575):
        balance = DescoAPI(i).balanceCheck()["balance"]
        monthlyUse = DescoAPI(i).balanceCheck()["currentMonthConsumption"]
        if int(balance) <= 250:
            await docID.send(
                f"Heyy, {balance}৳ Balance left in {i}. \n"
                + f"This month's consumption upto today is {monthlyUse}৳."
            )

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=nextcord.Game(next(statuses)))

@desco_balance_checker.before_loop
async def before_desco_balance_checker():
    await bot.wait_until_ready()

@change_status.before_loop
async def before_change_status():
    await bot.wait_until_ready()




if __name__ == "__main__":
    desco_balance_checker.start()
    change_status.start()
    bot.run(TOKEN)