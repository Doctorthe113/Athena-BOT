# author: @doctorthe113
# github: https://github.com/Doctorthe113/Athena-BOT
# version: 1.13.2


# built-in libraries
import asyncio
import io
import os
import json
import re
import sys
import threading
import random
from itertools import cycle
from collections import OrderedDict

# external libraries and apis
import nextcord
import psutil
import requests
import yt_dlp
import datetime
import googletrans

from nextcord import Interaction, Embed
from nextcord.ext import tasks, commands
from googletrans import Translator, LANGUAGES

# custom/local modules
from extentions import (
    Phrase,
    Web_Search,
    Nasa,
    Music_Player,
    Player_Buttons,
    Dropdown_View,
)


# * loading global variables
musicVcs: dict = {}  # {guild_id: voice_client_object}
logChannel: nextcord.TextChannel = None
statuses: OrderedDict = cycle(
    [
        "hello bbg 😏",
        "in your walls 👀",
        "Doctor chan my beloved 😍",
        "Yo Anna, where you at?",
        "Currently hosted on the cloud \\o/",
    ]
)

TOKEN: str = os.getenv(key="TOKEN")
GOOGLE_API: str = os.getenv(key="googleAPI")
CSE_ID: str = os.getenv(key="searchEngineID")
NASA_API: str = os.getenv(key="nasaAPI")
NINJA_API: str = os.getenv(key="ninjaAPI")
REDDIT_CLIENT: str = os.getenv(key="redditClient")
REDDIT_SECRET: str = os.getenv(key="redditSecret")
EMOJI_REGEX: re = re.compile(pattern=(r"<:(\w+):(\d+)>"))
URL_REGEX: re = re.compile(
    pattern=r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
)
PUNC_REGEX: re = re.compile(r"(?<!\A)[^\w\s]")


# * loading different classes and etcs
translator: Translator = Translator()
phraseObj: Phrase = Phrase()
webSearchObj: Web_Search = Web_Search(apiKey=GOOGLE_API, cseId=CSE_ID)
nasaObj: Nasa = Nasa(apiKey=NASA_API)
musicPlaybackObj: Music_Player = Music_Player()

intents: nextcord.Intents = nextcord.Intents.default()
intents.message_content = True
bot: nextcord.Client = commands.Bot(command_prefix=phraseObj.PREFIX, intents=intents)
bot.remove_command("help")


@bot.event
async def on_ready():
    loginTime: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    global logChannel
    logChannel = await bot.fetch_channel(1115589968929239153)

    print(f"{loginTime}: Logged in as {bot.user}")
    thread: int = threading.active_count()
    print(f"Current active thread count: {thread}")


@bot.event
async def on_message(rawMsg: nextcord.Message):
    with open("./db/guild.json", "r") as magic:
        guilds = json.load(magic)
    translateGuilds: list = guilds["translate"]
    dadJokeGuilds: list = guilds["dadPrompts"]
    uwuGuilds: list = guilds["uwuPrompts"]
    logGuilds: list = guilds["logs"]

    currentTime: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msgChannelId: int = rawMsg.channel.id
    randomChance: int = random.randint(1, 10)

    # filtering messages for future
    filteredMsg: str = re.sub(EMOJI_REGEX, "", rawMsg.content)
    filteredMsg: str = re.sub(URL_REGEX, "", filteredMsg)
    filteredMsgPunc: str = re.sub(PUNC_REGEX, "", filteredMsg)
    filteredMsgLow: str = filteredMsgPunc.lower()
    filteredMsgLowSet: set = set(filteredMsgLow.split())

    # skips if message author is bot itself
    if rawMsg.author == bot.user:
        return None

    # skips if message content is none
    if not filteredMsg:
        return None

    # logging messages
    if rawMsg.channel != logChannel and msgChannelId not in logGuilds:
        await logChannel.send(
            f"{currentTime}: {rawMsg.author.name} -> {rawMsg.content}"
        )

    # *For non-prompt/automated responses
    # translating messages
    translate: bool = False
    if msgChannelId in translateGuilds:
        if (
            translator.detect(filteredMsg).lang != "en"
            and not filteredMsgLowSet.intersection(phraseObj.UWUPROMPT)
            and not filteredMsgLow.startswith(phraseObj.PREFIX)
        ):
            translate = True

    if translate:
        translation: googletrans.models.Translated = translator.translate(filteredMsg)
        translationSrc: str = LANGUAGES.get(translation.src)
        replyMsg: nextcord.Message = await rawMsg.reply(
            f"*__From {translationSrc}__*\n>>> {translation.text}", mention_author=False
        )
        await replyMsg.add_reaction("❌")
        if randomChance == 2:
            instructMsg: nextcord.Message = await replyMsg.reply(
                "(*React with ❌ to delete wrong translations*)", mention_author=False
            )

        def check(reaction, user):
            return (
                user == rawMsg.author
                and str(reaction.emoji) == "❌"
                and reaction.message.id == replyMsg.id
            )

        try:
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=30.0, check=check
            )
            await replyMsg.delete()
            await instructMsg.delete()
        except nextcord.errors.Forbidden as e:
            await replyMsg.channel.send(f"Error deleting the message: {e}")
        except UnboundLocalError:
            pass
        except asyncio.TimeoutError:
            await replyMsg.remove_reaction("❌", bot.user)
            try:
                await instructMsg.delete()
            except UnboundLocalError:
                pass

    # saying hi/hello
    if filteredMsgLow == phraseObj.GREETINGPROMPT:
        greet: str = phraseObj.greeting_method()
        await rawMsg.channel.send(greet)

    # magic 8 ball
    if filteredMsgLow.startswith(phraseObj.MAGIC8BALLPROMPT):
        magic: str = phraseObj.magic8ball_method()
        await rawMsg.reply(magic)
        return None

    # rolling a dice
    if filteredMsgLow == "roll a dice":
        dice: int = phraseObj.roll_dice_method()
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
                jokePart: str = filteredMsgLow.partition(i)[-1]
                await rawMsg.reply(f"Hi,{jokePart}, I am Athena!", mention_author=False)

    # uwu roasts
    if msgChannelId not in uwuGuilds:
        for i in phraseObj.UWUPROMPT:
            if randomChance == 2 and i in filteredMsgLow:
                roast: str = phraseObj.uwu_roast_method()
                await rawMsg.reply(roast)

    # for mentions
    if filteredMsgLow == "athena":
        await rawMsg.reply("Hey that's me! 🙋‍♀️")

    await bot.process_commands(rawMsg)


# * For commands
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
@bot.command(aliases=["I"])
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
    if not (arg.startswith("for") and arg.endswith(" on wikipedia")):
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
    ytdlVid = yt_dlp.YoutubeDL(
        {
            "format": "best",
            "outtml": "-",
            "quiet": True,
        }
    )
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
    age = phraseObj.agify()
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


# for finding rhyming words. eg: "rhyme"
@bot.command()
async def rhyme(ctx, *, arg):
    words = phraseObj.rhyme(NINJA_API, arg)
    await ctx.send(f"__**Here are few words that rhyme with {arg}:**__```\n{words}```")


# for finding reddit posts. eg: "reddit {x}"
@bot.command()
async def reddit(ctx, *, arg):
    validSubReddits = [
        "cute",
        "naturegifs",
        "wholesomememes",
        "animalsbeingbros",
        "aww",
    ]
    if arg.lower() in validSubReddits:
        result = webSearchObj.reddit(REDDIT_CLIENT, REDDIT_SECRET, arg)
        await ctx.send(f"[{arg}]({result})")
    else:
        await ctx.send("Not a valid subreddit 😔. Run $help to find it :3")


@bot.command()
async def update(ctx):
    if ctx.author.id != 699342617095438479:
        return None
    await ctx.send("Updating...")
    try:
        currentProccess = sys.executable
        dbBakChannel = await bot.fetch_channel(1274034997086654486)
        await dbBakChannel.send(file=nextcord.File("./db/ping-res.json"))
        await dbBakChannel.send(file=nextcord.File("./db/guild.json"))
        # os.system("git stash push ./db/*")
        os.system("git fetch")
        os.system("git reset --hard origin/prod")
        # os.system("git stash apply")
        # os.system("git stash drop")
        os.system("pip3 install --break-system-packages --upgrade -r requirements.txt")
        await ctx.send("Updated!")
        os.execl(currentProccess, currentProccess, *sys.argv)
    except:
        await ctx.send("Unable to update. Please check console!")


# * Slash Commands
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


# disables logging in a specific channel
@bot.slash_command(name="log", description="Enables/Disables logging in this channel")
async def log(interaction: Interaction):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.id == 699342617095438479
    ):
        return await interaction.response.send_message(
            "You don't have permission to use this command!", ephemeral=True
        )

    with open("./db/guild.json", "r") as foo:
        guilds = json.load(foo)
    if interaction.channel.id in guilds["logs"]:
        guilds["logs"].remove(interaction.channel.id)
        with open("./db/guild.json", "w") as foo:
            json.dump(guilds, foo, indent=4)
        return await interaction.response.send_message(
            "Logging was disabled, now enabled.", ephemeral=True
        )

    guilds["logs"].append(interaction.channel.id)
    with open("./db/guild.json", "w") as foo:
        json.dump(guilds, foo, indent=4)
    return await interaction.response.send_message(
        "Logging was enabled, now disabled.", ephemeral=True
    )


# disables uwu roasts in a specific channel
@bot.slash_command(
    name="uwu", description="Enables/Disables uwu roasts in this channel"
)
async def log(interaction: Interaction):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.id == 699342617095438479
    ):
        return await interaction.response.send_message(
            "You don't have permission to use this command!", ephemeral=True
        )

    with open("./db/guild.json", "r") as foo:
        guilds = json.load(foo)
    if interaction.channel.id in guilds["uwuPrompts"]:
        guilds["uwuPrompts"].remove(interaction.channel.id)
        with open("./db/guild.json", "w") as foo:
            json.dump(guilds, foo, indent=4)
        return await interaction.response.send_message(
            "UwU roasts were disables, now enabled.", ephemeral=True
        )

    guilds["uwuPrompts"].append(interaction.channel.id)
    with open("./db/guild.json", "w") as foo:
        json.dump(guilds, foo, indent=4)
    return await interaction.response.send_message(
        "UwU roasts were enabled, now disabled.", ephemeral=True
    )


#  disables dad jokes in a specific channel
@bot.slash_command(name="dad", description="Enables/Disables dad jokes in this channel")
async def log(interaction: Interaction):
    if not (
        interaction.user.guild_permissions.manage_guild
        or interaction.user.id == 699342617095438479
    ):
        return await interaction.response.send_message(
            "You don't have permission to use this command!", ephemeral=True
        )

    with open("./db/guild.json", "r") as foo:
        guilds = json.load(foo)
    if interaction.channel.id in guilds["dadPrompts"]:
        guilds["dadPrompts"].remove(interaction.channel.id)
        with open("./db/guild.json", "w") as foo:
            json.dump(guilds, foo, indent=4)
        return await interaction.response.send_message(
            "Dad jokes were disables, now enabled.", ephemeral=True
        )

    guilds["dadPrompts"].append(interaction.channel.id)
    with open("./db/guild.json", "w") as foo:
        json.dump(guilds, foo, indent=4)
    return await interaction.response.send_message(
        "Dad jokes were enabled, now disabled.", ephemeral=True
    )


# music player starter
@bot.slash_command(name="music_player", description="Intiates the music player")
async def music_player(interaction: Interaction):
    try:
        musicVc: nextcord.VoiceClient = await interaction.user.voice.channel.connect()
        embed: nextcord.Embed = await musicPlaybackObj.embed_maker(
            "Music player",
            ("Songs in queue", ""),
            ("Currently playing <:player:1214062123953422386>", ""),
            ("", ""),
        )
        embedMsg: nextcord.Message = await interaction.response.send_message(
            embed=embed, view=Player_Buttons(musicPlaybackObj, musicVc)
        )

        musicVcs[interaction.guild.id] = [musicVc]
        musicPlaybackObj.queue_make(interaction.guild, musicVc, embedMsg)
    except:
        await interaction.response.send_message(
            "An error occurred, please try again!", ephemeral=True
        )


# music search
@bot.slash_command(name="music_search", description="Searches for a song")
async def music_search(interaction: Interaction, query: str):
    data: tuple = musicPlaybackObj.music_search(query)
    titles: str = "\n".join(f"{i}. {s}" for i, s in enumerate(data[0]))
    embed: Embed = await musicPlaybackObj.embed_maker(
        "Song finder", ("Titles", titles), ("", ""), ("", "")
    )
    await interaction.response.send_message(
        embed=embed,
        view=Dropdown_View(data[1], musicPlaybackObj),
        ephemeral=True,
    )


# music adder using url
@bot.slash_command(name="music_add", description="Adds song(s) using links only")
async def music_add(interaction: Interaction, url: str):
    try:
        await interaction.response.send_message("Song(s) added!", ephemeral=True)
        await musicPlaybackObj.queue_add_handler(interaction.guild, url)
    except:
        await interaction.response.send_message(
            "Please use a valid url!", ephemeral=True
        )


# to check queue if it exceeds embed limit
@bot.slash_command(name="music_queue_show", description="Shows the queue")
async def music_queue_show(interaction: Interaction):
    titles: list = musicPlaybackObj.queue_grab(interaction.guild)[1]
    queueList: str = "\n".join(f"{i}. {s}" for i, s in enumerate(titles))
    try:
        await interaction.response.send_message(queueList, ephemeral=True)
    except nextcord.errors.HTTPException:
        await interaction.response.send_message(
            "Queue is too big for discord a message!", ephemeral=True
        )


# music player stopper
@bot.slash_command(name="music_stop", description="Stops the music player")
async def music_stop(interaction: Interaction):
    try:
        musicVc = musicVcs[interaction.guild.id][0]
        await musicPlaybackObj.queue_del(interaction.guild)
        await musicVc.disconnect()
        await interaction.response.send_message("Music player stopped!")
    except:
        await interaction.response.send_message("I am not playing music!")


# * Other functions that needs to run periodically
# check my electric meter balance
@tasks.loop(hours=12)
async def desco_balance_checker():
    descoChannel = await bot.fetch_channel(1273571248554905621)
    for i in ((661120206515, 12021574), (661120206516, 12021575)):
        balance = webSearchObj.desco_bill(i[0], i[1])
        if int(balance) <= 250:
            await descoChannel.send(f"Balance {balance} left in {i[1]}")


@desco_balance_checker.before_loop
async def before_desco_balance_checker():
    await bot.wait_until_ready()


# to change status
@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=nextcord.Game(next(statuses)))


@change_status.before_loop
async def before_change_status():
    await bot.wait_until_ready()


@tasks.loop(hours=6)
async def ping_doc():
    todayDate = datetime.datetime.now().strftime("%Y-%m-%d")
    pingChannel = await bot.fetch_channel(1273569772407226400)

    # check if today's entry in db or not. `init = true` to check for today's entry
    # `init = false` to check for previous days entry
    def db_check(init):
        with open("./db/ping-res.json", "r") as foo:
            pingDb = json.load(foo)

        if init:
            if todayDate in pingDb:
                return True
            else:
                return False

        # checks for previous days entry
        global missedWeek, missedMonth, missedThreeMonths
        missedDay = 0
        missedWeek = False
        missedMonth = False
        missedThreeMonths = False

        newPingDb = OrderedDict(pingDb)
        for key, value in reversed(newPingDb.items()):
            if not value:
                missedDay += 1
            else:
                missedDay = 0
                break

            if missedDay == 7:
                missedWeek = True
            if missedDay == 30:
                missedMonth = True
            if missedDay == 90:
                missedThreeMonths = True

        return missedWeek, missedMonth, missedThreeMonths

    # write today's entry in db
    def db_write(ping):
        with open("./db/ping-res.json", "r") as foo:
            pingDb = json.load(foo)

        with open("./db/ping-res.json", "w") as foo:
            pingDb.update({todayDate: ping})
            json.dump(pingDb, foo, indent=4)

    # check if user responded or not
    def check(reaction, user):
        return user != bot.user and str(reaction.emoji) == "✅"

    # first checks if there's an entry for today or not
    if db_check(True):
        return None
    pingMsg = await pingChannel.send(
        f"Pinging <@699342617095438479>! Please react if you are okay."
    )
    await pingMsg.add_reaction("✅")

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=28800, check=check)
        db_write(True)
        await pingMsg.edit(content="Response recieved. Thank you!")
    except asyncio.TimeoutError:
        await pingMsg.edit(content="No response. Adding it to the DB!")
        db_write(False)
        missedWeek, missedMonth, missedThreeMonths = db_check(False)

        if missedWeek:
            await pingChannel.send(
                "Missed ping in the last week! Assuming you were busy!"
            )
        if missedMonth:
            await pingChannel.send(
                "Missed ping in the last month! Assuming you are in trouble!"
            )
        if missedThreeMonths:
            await pingChannel.send(
                "Missed ping in the last 3 months! Assuming you are dead!"
            )


@ping_doc.before_loop
async def before_ping_doc():
    await bot.wait_until_ready()


# # to wish happy birthday
# @tasks.loop(seconds=30)
# async def birthday_reminder():
#     birthdayMessages = [
#         "Wishing you a day filled with laughter and joy. May your birthday be as wonderful as you are!",
#         "Happy Birthday! May your special day be packed with all the happiness, peace, and love you deserve.",
#         "On your birthday, I hope that you sit back and relax, let joy and tranquility take the lead, and make this day one to remember!",
#         "Cheers to another year of fabulous you! Keep shining and spreading positivity. Happy Birthday!",
#         "May your birthday be the start of a year filled with good luck, good health, and much happiness.",
#         "Sending you smiles for every moment of your special day. Have a wonderful time and a very happy birthday!",
#         "Hope your birthday is just the beginning of a year full of happiness and success. Have a great day ahead!",
#         "Happy Birthday! May each hour and minute be filled with delight, and your special day be perfect!",
#         "On your birthday, I wish you a lifetime of joy, a smaller amount of worries, and a boatload of big dreams coming true.",
#         "A toast to you on your birthday! May you live to be old and toothless, surrounded by love and joy forever.",
#     ]
#     today = datetime.datetime.now(datetime.UTC)
#     today = today.strftime("%d %B %H:%M")
#     if today == "18 May 00:00":
#         birthDayUser = await bot.fetch_user(836200807446741002)
#     elif today == "03 June 00:00":
#         birthDayUser = await bot.fetch_user(820476981480914984)
#     else:
#         return None
#     # if random.randint(1, 3) == 2:
#     randomMsg = random.choice(birthdayMessages)
#     await birthDayUser.send(randomMsg)
#     docID = await bot.fetch_user(699342617095438479)
#     await docID.send(randomMsg)
#     # else:
#     #     return None


# @birthday_reminder.before_loop
# async def before_birthday_reminder():
#     await bot.wait_until_ready()


if __name__ == "__main__":
    change_status.start()
    ping_doc.start()
    desco_balance_checker.start()
    # birthday_reminder.start()
    bot.run(TOKEN)


# # for starting music playback. eg: "join"
# @bot.command()
# async def join(ctx):
#     try:
#         vc = await ctx.author.voice.channel.connect()
#         vcs[vc.guild.id] = vc
#         dj = ctx.author.name
#         queue_make(vc)
#         await ctx.send(f"Joined {dj}'s voice channel!")
#     except AttributeError:
#         await ctx.send("You haven't joined a voice channel yet, silly! 😒")


# # for stopping music playback. eg: "stop"
# @bot.command()
# async def stop(ctx):
#     vc = vcs[ctx.guild.id]
#     try:
#         await vc.disconnect()
#         await ctx.send("Stopped the music playback, cya later! 😊")
#         del vcs[ctx.guild.id]
#         queue_del(vc)
#     except:
#         await ctx.send("I am unable to properly stop the music 😔")


# # for adding music to the queue. eg: "add https://www.youtube.com/watch?v=x"
# @bot.command()
# async def add(ctx, *, arg):
#     vc = vcs[ctx.guild.id]
#     title = music_playbackObj.music_search(arg, vc)
#     await ctx.send(f"Added __{title}__ to the queue.")


# # for starting/playing music. eg: "play"
# @bot.command()
# async def play(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#     except:
#         await ctx.send("I am not connected to a voice channel 😔")
#         return None
#     if not vc.is_playing():
#         queue = queue_grab(vc)
#         songURL = queue[0][0]
#         track = nextcord.FFmpegPCMAudio(songURL, **FFMPEG_OPTIONS)
#         vc.play(track, after=lambda e: queue_check(vc))
#         await ctx.send(f"Started playing...")
#     else:
#         await ctx.send("I am already playing! Use `athena add` to add music.")


# # for pausing music. eg: "pause"
# @bot.command()
# async def pause(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#         vc.pause()
#         await ctx.send("Paused!")
#     except:
#         await ctx.send("I am not playing anything right now 😔")


# # for resuming music. eg: "resume"
# @bot.command()
# async def resume(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#         vc.resume()
#         await ctx.send("Resumed!")
#     except:
#         await ctx.send("I have not anything paused right now 😀")


# # for looping music. eg: "loop"
# @bot.command()
# async def loop(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#         loop = queue_loop(vc)
#         if loop:
#             await ctx.send("Looping the current queue!")
#         else:
#             await ctx.send("Turned loop off!")
#     except:
#         await ctx.send("I am unable to loop 😔")


# # for skipping music. eg: "skip"
# @bot.command()
# async def skip(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#     except:
#         await ctx.send("I am not connected to a voice channel 😔")
#     if not vc.is_playing() or not vc:
#         await ctx.send("I am not playing anything right now 😔")
#     else:
#         vc.pause()
#         await queue_check(vc)
#         await ctx.send("Skipping!")


# # for checking queue. eg: "queue"
# @bot.command()
# async def queue(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#         queue = queue_grab(vc)
#         queue = queue[1]
#         queueList = ""
#         for i, j in enumerate(queue):
#             queueList = queueList + f"{i}. {j}\n"
#         await ctx.send(f"Here's the queue:```md\n{queueList}```")
#     except:
#         await ctx.send("Queue is empty.")


# # for shuffling queue. eg: "shuffle"
# @bot.command()
# async def shuffle(ctx):
#     try:
#         vc = vcs[ctx.guild.id]
#         queue_shuffle(vc)
#         queue = queue_grab(vc)
#         queue = queue[1]
#         queueList = ""
#         for i, j in enumerate(queue):
#             queueList = queueList + f"{i}. {j}\n"
#         await ctx.send(f"Queue shuffled! Here's new queue:```md\n{queueList}```")
#     except:
#         await ctx.send("I am unable to shuffle 😔")


# # for removing a song from the queue. eg: "remove 1"
# @bot.command()
# async def remove(ctx, index):
#     try:
#         vc = vcs[ctx.guild.id]
#         index = int(index)
#         removedSong = queue_remove(vc, index)
#         await ctx.send(f"Removed __{removedSong}__ from the queue.")
#     except:
#         await ctx.send(f"I am unable to remove {index}th song 😔")
