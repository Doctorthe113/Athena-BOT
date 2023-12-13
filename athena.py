# built-in libraries
import os, json, re, threading, random
# external libraries and apis
import nextcord, psutil

from nextcord import Interaction
from nextcord.ext import tasks
from googletrans import Translator, LANGUAGES
from dotenv import load_dotenv
from datetime import datetime
from phrases import phrase
from extentions.web_search import webSearch
from extentions.desco import descoAPI

# loading global variables
load_dotenv()
TOKEN = os.getenv("TOKEN")
APIKEY = os.getenv("googleApiKey")
CSEID = os.getenv("searchEngineID")
EMOJIREGEX = re.compile((r"<:(\w+):(\d+)>"))
LOGCHANNEL = None

# loading differebnt classes and etcs
intents = nextcord.Intents.default()
intents.message_content = True
client = nextcord.Client(intents=intents)

translator = Translator()
phraseObj = phrase()
webSearchObj = webSearch(apiKey=APIKEY, cseId=CSEID)



@client.event
async def on_ready():
	loginTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	print(f"{loginTime}: Logged in as {client.user}")
	thread = threading.active_count()
	print(f"Current active thread count: {thread}")

	global LOGCHANNEL, DOCID
	LOGCHANNEL = await client.fetch_channel(1115589968929239153)



@client.event
async def on_message(rawMsg):
	with open("guild.json", "r") as foo:
			guilds = json.load(foo)
	translateGuilds = guilds["translate"]
	dadJokeGuilds = guilds["dadPrompts"]
	uwuGuilds = guilds["uwuPrompts"]


	currentTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msgChannelID = rawMsg.channel.id
	randomChance = random.randint(1, 3)


	# filtering messages for future
	filteredMsgNoEmoji = re.sub(EMOJIREGEX, "", rawMsg.content)
	filteredMsg = filteredMsgNoEmoji.translate(str.maketrans("", "", "\"\',.:;?\\~"))
	filteredMsgLow = filteredMsg.lower()
	filteredMsgSet = set(filteredMsgLow.split())


	# skips if message author is bot itself
	if rawMsg.author == client.user:
			return None


	# skips if message content is none
	if filteredMsg == "" or filteredMsg == None:
			return None


	# logging messages
	if rawMsg.channel != LOGCHANNEL:
			await LOGCHANNEL.send(f"{currentTime}: {rawMsg.author.name} -> {rawMsg.content}")


	# *For non-prompt/automated responses
	# translating messages
	if msgChannelID in translateGuilds:
			if (translator.detect(filteredMsg).lang != "en" and
					not filteredMsgSet.intersection(phraseObj.UWUPROMPT)):
					translateMsg = translator.translate(filteredMsgNoEmoji)
					translateMsgSrc = LANGUAGES.get(translateMsg.src)
					await rawMsg.reply(f"*From {translateMsgSrc}* \n>>> {translateMsg.text}",
															mention_author=False)
					return None


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
	if msgChannelID not in dadJokeGuilds:
			for i in phraseObj.DADPROMPT:
					if randomChance != 2:
							return None
					if filteredMsgLow.startswith(i):
							bar = filteredMsgLow.partition(i)[-1]
							await rawMsg.reply(f"Hi, {bar}, I am Athena!", mention_author=False)
							return None


	# uwu roasts
	if msgChannelID not in uwuGuilds:
			for i in phraseObj.UWUPROMPT:
					if randomChance != 2:
							return None
					if i in filteredMsgLow:
							bar = phraseObj.uwuRoastMethod()
							await rawMsg.reply(bar)
							return None



# *Prompt based non-slash commands
	for prompt in phraseObj.PROMPT:
			# telling dad jokes
			if (filteredMsgLow.startswith(f"{prompt} tell me a joke") or
					filteredMsgLow.startswith(f"{prompt} tell me a dad joke")):
					await rawMsg.reply(phraseObj.dadJokeMethod())
					break


			# checking system
			if filteredMsgLow.startswith(f"{prompt} check system"):
					thread = threading.active_count()
					process = psutil.Process(os.getpid())
					memoryUsage = round(process.memory_info().rss / 1048576, 2)
					await rawMsg.reply(f"Thread: {thread}, Memory: {memoryUsage} MB")
					break


			# json validator
			if filteredMsgLow.startswith(f"{prompt} validate this json"):
					jsonForCheck = re.sub(r"^```json\n|```$", "", rawMsg.content)
					try:
							baz = json.loads(jsonForCheck)
							await rawMsg.reply("This json is valid.", mention_author=False)
					except ValueError as e:
							await  rawMsg.reply(f"This json isn't valid. ```{e}```")
							break


			# google search
			if filteredMsgLow.startswith(f"{prompt} what is"):
					query = re.sub(f"{prompt} what is", "", rawMsg.content, flags=re.IGNORECASE)
					result = webSearchObj.google_search(query)
					await rawMsg.reply(result)
					break

			if (filteredMsgLow.startswith(f"{prompt} search for") and
					filteredMsgLow.endswith("on google")):
					query = re.sub(f"^{prompt} search for | on google$", "", rawMsg.content,
													flags=re.IGNORECASE)
					result = webSearchObj.google_search(query)
					await rawMsg.reply(result)
					break


			# wikipedia search
			if (filteredMsgLow.startswith(f"{prompt} search for") and
					filteredMsgLow.endswith("on wikipedia")):
					query = re.sub(f"^{prompt} search for | on wikipedia$", "", filteredMsg,
													flags=re.IGNORECASE)
					wikiSummary = webSearchObj.wikiSearch(query)[0]
					relatedArticles = webSearchObj.wikiSearch(query)[1]
					relatedArticles = chr(10).join(relatedArticles)
					await rawMsg.reply(f"**__Related titles:__** \n```{relatedArticles}  ```",
															mention_author=False)
					await rawMsg.reply(f"**__Summary of your query__**: \n```{wikiSummary} ```")
					break


			# purging messages
			if (filteredMsgLow.startswith(f"{prompt} purge") and
					rawMsg.author.guild_permissions.manage_messages):
					numOfMsg = re.sub(f"{prompt} purge", "", filteredMsgLow)
					await rawMsg.message.channel.send(f"{numOfMsg} messages purged.")
					await rawMsg.channel.purge(limit = int(numOfMsg) + 2)
					break


			# defining words
			if filteredMsgLow.startswith(f"{prompt} define"):
					query = re.sub(f"{prompt} define", "", filteredMsg)
					result = webSearchObj.dictionary(query)
					await rawMsg.reply(f"### {result[0]} \n" +
															f"### {result[1]} \n" +
															f"__Pronounciation__: {result[2]} \n" +
															f"__Origin__: {result[3]} \n" +
															f"__Definitions__:{result[4]}")
					break


			# replying to mentions
			if filteredMsgLow == prompt:
					await rawMsg.reply("Hey that's me! 🙋‍♀️")
					break



# slash command for feedback:
@client.slash_command(name="feedback", description="Let's you send feedback directly.")
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
async def descoBalanceChecker():
	DOCID = await client.fetch_user(699342617095438479)
	for i in (12021574, 12021575):
			balance = descoAPI(i).balanceCheck()["balance"]
			monthlyUse = descoAPI(i).balanceCheck()["currentMonthConsumption"]
			if int(balance) <= 250:
					await DOCID.send(f"Heyy, {balance}৳ Balance left in {i}. \n" +
												f"This month's consumption upto today is {monthlyUse}৳.")

# @descoBalanceChecker.before_loop
# async def before_descoBalanceChecker(self):
#     await self.bot.wait_until_ready()








descoBalanceChecker.start()
client.run(TOKEN)