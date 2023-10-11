import random, json, re, asyncio, datetime, threading # built-in libraries
import nextcord, wikipedia, psutil, matplotlib # external libraries and apis
import features.response, features.calc, features.google_search, features.dictionary, features.desco # homemade modules


from nextcord import Interaction, SlashOption # for slash commands
from io import BytesIO # for storing the plot from eq_solver in buffer
from googletrans import Translator, LANGUAGES # for tranlation ofc
from nextcord.ext import tasks

with open("keys.json", "r") as f:
    token = json.load(f)


intents = nextcord.Intents.default()
intents.message_content = True
client = nextcord.Client(intents=intents)

translator = Translator()



@client.event
async def on_ready():
    utc_6_time = datetime.datetime.now()
    formatted_time = utc_6_time.strftime("%Y-%m-%d %H:%M:%S")

    print(f"{formatted_time}        Logged in as {client.user}")
    thread = threading.active_count()
    print(f"Current active thread count: {thread}")



@client.event
async def on_message(message):
    with open("guild.json", "r") as f:
        guilds = json.load(f)

    messages = message.content
    messages = messages.lower()
    messages = messages.translate(str.maketrans("","","!\"\',.:;?\\~"))
    # instead of string.punctuation. 
    # Im just writing the punctuations like this Because `string.puncuation` would delete the punctuations I didnt want to delete.
    utc_time = datetime.datetime.now()
    formatted_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
    log_channel = await client.fetch_channel(1115589968929239153)


    if message.author == client.user:
        return
    if message.channel != log_channel:
        await log_channel.send(f"{formatted_time}(UTC +6)        {message.author.name} -> {message.content}") # type: ignore # type: ignore # this is to log messages with time.

    if str(message.channel.id) in guilds["translate"]:
        if translator.detect(message.content).lang != "en" and "uwu" not in messages and "owo" not in messages:
            translated_msg = translator.translate(message.content)
            await message.reply(f"`{message.author.name} from {LANGUAGES.get(translated_msg.src)}` ```{translated_msg.text}```", mention_author = False)
            return

    if messages.startswith(tuple(features.response.greetings)):
        reply = random.choice(list(features.response.greetings_response))
        reply = reply.capitalize()
        await message.reply(reply)

    if messages.startswith(tuple(features.response.magic8ball_input)):
        result = random.choice(list(features.response.magic8ball))
        await message.reply(result)
        return

    if messages == "roll a dice":
        dice = random.randint(1, 6)
        await message.reply(f"🎲 {dice} 🎲 ")
        return

    if messages == "ping":
        await message.reply(f"Pong! Bot Latency `{round(client.latency * 1000)} ms`")
        return

    for dad in (features.response.dad_words):
        dad_word = guilds["dad_words"]

        if dad in messages and str(message.channel.id) not in list(dad_word):
            dad_reply = messages.partition(dad)[-1] #we use partition() to remove the first "i am" appears in the message. 
            await message.reply(f"Hi, {dad_reply}, I am Athena!", mention_author = False)
            break

    for dadStart in (features.response.dad_wordStart):
        dad_word = guilds["dad_words"]

        if messages.startswith(dadStart) and str(message.channel.id) not in list(dad_word):
            dad_reply_start = messages.partition(dadStart)[-1]
            await message.reply(f"Hi, {dad_reply_start}, I am Athena!", mention_author = False)
            break

    for owo in (features.response.uwu):
        uwu_words = guilds["uwu_words"]

        if owo in messages and str(message.channel.id) not in list(uwu_words):
            await message.reply(random.choice(list(features.response.uwu_roasts)))
            return




    for prompt in features.response.athena_prompt: # using for loop then if to check if the user message have the prompts or not.
        if prompt not in messages: # skips the iteration if prompt words are not in the message
            continue


        if messages.startswith(f"{prompt} tell me a dad joke") or messages.startswith(f"{prompt} tell me a joke"): #Because cant use tuple or list with .startswith()
            await message.reply(random.choice(list(features.response.dad_jokes)))
            break


        if messages.startswith(f"{prompt} search for ") and messages.endswith("on wikipedia"):
            wiki_query = re.sub(f"^{prompt} search for | on wikipedia$", "", messages)

            await message.reply(f"Heres a list of of relavent articles on Wikipedia you might be interested in: ``` {chr(10).join(wikipedia.search(wiki_query))} ```") 
            #we use chr(10)[equivelant to \n].join() to combine the list and then seperate each part by a new line
            try:
                await message.reply(f"Here's the summary for {wiki_query}: ``` {wikipedia.summary(wiki_query, chars = 2000, auto_suggest = False)} ```")
            except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as error:
                await message.reply(f"I am sorry I could not fetch the article you were looking. Error: ``` {error} ```. Perhaps try a different keyword from the list above?")
                
                def wiki_reply(wiki_reply):
                    return wiki_reply.author == message.author and wiki_reply.channel == message.channel
                try: 
                    wiki_error_handling = await client.wait_for("message", check = wiki_reply, timeout = 60)
                    await message.reply(f"Here is the summary of {wiki_error_handling.content}: ``` {wikipedia.summary(wiki_error_handling.content, chars = 2000, auto_suggest = False, redirect = True)} ```")
                except asyncio.TimeoutError:
                    await message.reply("Timedout! You didn\'t reply in 60 seconds :(")

            break


        if messages.startswith(f"{prompt} search for ") and messages.endswith(f"on google"):
            keyword = re.sub(f"^{prompt} search for | on google$", "", messages)

            snippets = features.google_search.google_search(keyword)
            await message.reply(f"Here's your search results: {snippets}")

            break


        if messages.startswith(f"{prompt} what is "):
            keyword = re.sub(f"{prompt} what is ", "", messages)

            snippets = features.google_search.google_search(keyword)
            await message.reply(f"Here's your search results: {snippets}")

            break


        if messages.startswith(f"{prompt} validate this json"):
            await message.reply("Please send the JSON(***not JSON file***) after this message inside a codeblock. (Within 2 minutes.)")

            def json_reply(json_reply):
                return json_reply.author == message.author and json_reply.channel == message.channel
            try:
                json_data = await client.wait_for("message", check = json_reply, timeout = 120)
                json_to_check = re.sub(r"^```json\n|\n```$", "", json_data.content)
                try:
                    validate_json = json.loads(f"{json_to_check}")
                    await message.reply("This JSON is valid.")
                except (ValueError, UnicodeDecodeError) as json_error:
                    await message.reply(f"I am afraid this JSON is invalid, error = ``` {json_error} ```")

            except asyncio.TimeoutError:
                await message.reply("Timedout! You didn\'t send the JSON in 120 seconds :(")

            break


        if messages.startswith(f"{prompt} purge"):
            if message.author.guild_permissions.manage_messages:
                purge_length = re.sub(f"{prompt} purge", "", messages)
                await message.channel.send(f"{purge_length} messages purged.")
                await message.channel.purge(limit = int(purge_length) + 2)
                break


        if messages == f"{prompt} check system":
            thread = threading.active_count()
            memory = psutil.virtual_memory()[3]/1000000
            memory_percentage = psutil.virtual_memory()[2]

            await message.reply(f"""    Thread: {thread} 
    Memory used: {memory} Mb
    Memory usage: {memory_percentage}""")
            break


        if messages.startswith(f"{prompt} define"):
            keyword = re.sub(f"{prompt} define", "", messages)
            dictionary_result = features.dictionary.dictionary(keyword)
            await message.reply(dictionary_result)
            break


        if messages == prompt:
            await message.reply("Hey thats me! 👀")
            break




@client.slash_command(name = "disable_features", description = "Disable dad words(I\'m jokes) and UWU roasts.")
async def disable(interaction: Interaction, feature: int = SlashOption(name = "feature", choices = {"Dad words": 1, "UWU": 2, "Tranlate": 3})):
    if interaction.user.guild_permissions.manage_guild or interaction.user.id == 699342617095438479:
        with open("guild.json", "r") as f:
            guilds = json.load(f)
            dad_word_disabled_guilds = guilds["dad_words"]
            uwu_word_disabled_guilds = guilds["uwu_words"]
            translate = guilds["translate"]

        if feature == 1:
            dad_word_disabled_guilds.append(str(interaction.channel_id))
            await interaction.response.send_message("Done disabling!", ephemeral = True)

        if feature == 2:
            uwu_word_disabled_guilds.append(str(interaction.channel_id))
            await interaction.response.send_message("Done disabling!", ephemeral = True)

        if feature == 3:
            translate.remove(str(interaction.channel_id)) # we are removing for translate so it will be off by default
            await interaction.response.send_message("Done enabling!", ephemeral = True)

        with open("guild.json", "w") as f:
            json.dump(guilds, f)
    else: await interaction.response.send_message("You do not have the permission.")

@client.slash_command(name = "enable_features", description = "enable dad words(I\'m jokes) and UWU roasts.")
async def enable(interaction: Interaction, feature: int = SlashOption(name = "feature", choices = {"Dad words": 1, "UWU": 2, "Tranlate": 3})):
    if interaction.user.guild_permissions.manage_messages or interaction.user.id == 699342617095438479:
        with open("guild.json", "r") as f:
            guilds = json.load(f)
            dad_word_disabled_guilds = guilds["dad_words"]
            uwu_word_disabled_guilds = guilds["uwu_words"]
            translate = guilds["translate"]

        if feature == 1:
            dad_word_disabled_guilds.remove(str(interaction.channel_id))
            await interaction.response.send_message("Done enabling!", ephemeral = True)

        if feature == 2:
            uwu_word_disabled_guilds.remove(str(interaction.channel_id))
            await interaction.response.send_message("Done enabling!", ephemeral = True)

        if feature == 3:
            translate.append(str(interaction.channel_id)) # we are appending for translate so it will be off by default. Only enabled if we manually enable it
            await interaction.response.send_message("Done enabling!", ephemeral = True)

        with open("guild.json", "w") as f:
            json.dump(guilds, f)
    else: await interaction.response.send_message("You do not have the permission.")

@client.slash_command(name = "ping", description = "Ping the bot and get latency of the bot.")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"Pong! Bot Latency `{round(client.latency * 1000)} ms`") # type: ignore # type: ignore # type: ignore

@client.slash_command(name = "roll_dice", description = "Randomly generate a number between 1-6")
async def dice(interaction: Interaction):
    dice = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 {dice} 🎲 ") # type: ignore

@client.slash_command(name = "dad_joke", description = "Tells you dad joke.")
async def joke(interaction: Interaction):
    await interaction.response.send_message(random.choice(list(features.response.dad_jokes))) # type: ignore

@client.slash_command(name = "system_check", description = "Shows memory usages of the machine and thread count.")
async def system(interaction: Interaction):
    thread = threading.active_count()
    memory = psutil.virtual_memory()[3]/1000000
    memory_percentage = psutil.virtual_memory()[2]

    await interaction.response.send_message(f"""    Thread: {thread} 
    Memory used: {memory} Mb
    Memory usage: {memory_percentage}""")

@client.slash_command(name = "json_validator", description = "Validates JSONs. Don't use codeblock!")
async def json_valid(interaction: Interaction, arg: str):
    try:
        validate_json = json.loads(arg)
        await interaction.response.send_message("This JSON is valid.")
    except (ValueError, UnicodeDecodeError) as json_error:
        await interaction.response.send_message(f"I am afraid this JSON is invalid, error = ``` {json_error} ```")

@client.slash_command(name = "wiki", description = "Returns summary of Wikipedia articles. Case sensitive.")
async def wikipedia_summary(interaction: Interaction, arg: str):
    try:
        await interaction.response.send_message(f"Here's the summary for {arg}: ``` {wikipedia.summary(arg, chars = 2000, auto_suggest = False)} ```")
    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as error:
        await interaction.response.send_message(f"I am sorry I could not fetch the article you were looking. Error: ``` {error} ```. Perhaps try a different keyword from the list above?")

@client.slash_command(name = "purge", description = "Purges messages.")
async def purge(interaction: Interaction, arg: str):
    if interaction.user.guild_permissions.manage_messages or interaction.user.id == 699342617095438479: # type: ignore
        await interaction.response.send_message(f"{arg} messages purged.")
        await interaction.channel.purge(limit = int(arg) + 1) # type: ignore
    else: await interaction.response.send_message("You do not have the `manage_message` permission.")

@client.slash_command(name = "feedback", description = "Give feedback directly to The Doctor.")
async def feedback(interaction: Interaction, arg: str):
    feedback_channel = await client.fetch_channel(1126220831496863786)
    user_name = interaction.user.name
    try:
        await feedback_channel.send(f"By {user_name}, ``` {arg} ```") # type: ignore
        await interaction.response.send_message("Feedback sent.")
    except (nextcord.errors.ApplicationInvokeError, nextcord.errors.Forbidden, nextcord.errors.HTTPException) as error:
        await interaction.response.send_message(f"Feedback could not be sent. Error: ``` {error} ```")

@client.slash_command(name = "equation_solver", description = "Solves equations, currently in experimental phase, report any bugs and suggestions to The Doctor")
async def eq_solver(interaction: Interaction, arg: str):
    await interaction.response.defer() # To make the respond time last longer

    try:
        proccessed_equation = features.calc.symbol_conv(arg)
        x, y = "[]"
        x, y, plot = features.calc.eq_calc(proccessed_equation)

        try: 
            matplotlib.use("agg")
            matplotlib_backend = plot.backend(plot)
            matplotlib_backend.process_series()

            buffer = BytesIO()

            matplotlib_backend.fig.savefig(buffer, format = "png", bbox_inches="tight", pad_inches = 0)

            buffer.seek(0)

            await interaction.followup.send(f"Solution for X: `{str(x)}`, Solution for Y: `{str(y)}`, Here is the graph for the equation.", file = nextcord.File(buffer, "p.png"))

        except: 
            await interaction.followup.send(f"Solution for X: `{str(x)}`, Solution for Y: `{str(y)}`")
    except: await interaction.followup.send("An error occurred")

@client.slash_command(name = "multiplot", description = "Plots multiple equations, currently in experimental phase, report any bugs to The Doctor")
async def multiplot(interaction: Interaction, arg: str):
    try:
        await interaction.response.defer() # To make the respond time last longer

        proccessed_equation = features.calc.symbol_conv(arg)
        plot = features.calc.multiplot(proccessed_equation)

        matplotlib.use("agg")
        matplotlib_backend = plot.backend(plot)
        matplotlib_backend.process_series()

        buffer = BytesIO()

        matplotlib_backend.fig.savefig(buffer, format = "png", bbox_inches="tight", pad_inches = 0)

        buffer.seek(0)

        await interaction.followup.send(f"Here is the graph for the equation.", file = nextcord.File(buffer, "p.png"))
    except Exception as e:
        print(e)
        await interaction.followup.send("An error occurred")

@client.slash_command(name = "google_search", description = "Searches Google and returns 10 snippets and url of the top website")
async def google(interaction: Interaction, arg: str):
    try:
        snippets = features.google_search.google_search(arg)
        await interaction.response.send_message(f"Here's your search results: {snippets}")
    except Exception as e:
        await interaction.response.send_message(f"An error occured while Googling. ``` {e} ```")

@client.slash_command(name = "dictionary", description = "Looks for definitions.")
async def dictionary(interaction: Interaction, arg: str):
    dictionary_result = features.dictionary.dictionary(arg)
    await interaction.response.send_message(dictionary_result)




@tasks.loop(hours = 3)
async def balance_checker():
    Doc_ID = await client.fetch_user(699342617095438479)
    for i in [12021574, 12021575]:
        balance, month_usage = features.desco.check_balance(i)

        if int(balance) <= 150:
            await Doc_ID.send(f"Heyy, you need to pay the electricity bill in {i}, Doctor.")
            await Doc_ID.send(f"{balance}৳ Balance left in {i} and this month's consumption up to this day is {month_usage}৳.")

balance_checker.start()





client.run(token["TOKEN"])


utc_time = datetime.datetime.now()
formatted_time = utc_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time}        Bot logged out.")




# code dump:

# @tasks.loop(seconds = 10)
# async def Anna_birthday_msg():
#     Doc_ID = await client.fetch_user(699342617095438479)
#     Anna_ID = await client.fetch_user(820476981480914984)
#     utc_time = datetime.datetime.utcnow()
#     count = 0
#     if utc_time.day == 3 and utc_time.month == 6 and count == 0: 
#         await Anna_ID.send("""Happy birthday!!!! On your 20th birthday! You're an old lady now 😆. Anyhow enjoy this day, its your day after all! 
# I don't think I am allowed to say this but don't let any bitch ruin the day ;)
# Sincerely,
# Your truly Athena""")
#         await Doc_ID.send("Message Sent.")
#         Anna_birthday_msg.stop()
#         await Doc_ID.send("Loop stopped.")
#         count += 1

# @Anna_birthday_msg.before_loop
# async def before():
#     await client.wait_until_ready()
#     print("Finished waiting")

# async def setup_hook():
#     Anna_birthday_msg.start()

# client.setup_hook = setup_hook