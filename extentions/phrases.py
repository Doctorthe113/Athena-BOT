import random
import requests
class Phrase():
    def __init__(self) -> None:
        self.PREFIX = (
            "athena ",
            "hey athena ",
            "hi athena ",
            "hello athena ", 
            "sup athena ",
            "athena senpai ",
            "Athena ",
            "Hey Athena ",
            "Hi Athena ",
            "Hello Athena ", 
            "Sup Athena ",
            "Athena senpai ",
            "<@1085635807773208616> ",
            "$",
            "?"
        )
        self.GREETINGPROMPT = (
            "hi",
            "hello",
            "hemlo",
            "haii",
            "hai",
            "haiii",
            "greetings",
            "ello",
            "heyo",
            "hewo",
            "hewwo",
            "whats popping",
            "hey"
        )
        self.GREETINGRESPONSE = (
            "hi.",
            "hello.",
            "hemlo.",
            "haii.",
            "hai.",
            "haiii.",
            "greetings.",
            "ello.",
            "heyo.",
            "hewo.",
            "hewwo.",
            "Yo what\'s popping!",
            "whats popping.",
            "hi, how are you?",
            "hello, how are you doing on this fine day?",
            "hemlo, hru?",
            "haii, how are you?",
            "hai, how are you doing?",
            "greeting mortal :)"
        )
        self.MAGIC8BALLPROMPT = (
            "magic 8 ball",
            "magic 8ball",
            "8 ball",
            "8ball"
        )
        self.MAGIC8BALL = (
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don\'t count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        )
        self.DADPROMPT = (
            "im",
            "i am"
        )
        self.DADJOKE = (
            "I accidentally gave my wife gluestick instead of lipstick but she didn\'t complain later.",
            "I\'m afraid for the calendar. Its days are numbered.",
            "My wife said I should do lunges to stay in shape. That would be a big step forward.",
            "Why do fathers take an extra pair of socks when they go golfing?" "In case they get a hole in one!",
            "Singing in the shower is fun until you get soap in your mouth. Then it\'s a soap opera.",
            "What do a tick and the Eiffel Tower have in common?" "They\'re both Paris sites.",
            "What do you call a fish wearing a bowtie?" "Sofishticated.",
            "How do you follow Will Smith in the snow?" "You follow the fresh prints.",
            "If April showers bring May flowers, what do May flowers bring?" "Pilgrims.",
            "I thought the dryer was shrinking my clothes. Turns out it was the refrigerator all along.",
            "How does dry skin affect you at work?" "You don’t have any elbow grease to put into it.",
            "What do you call a factory that makes okay products?" "A satisfactory.",
            "Dear Math, grow up and solve your own problems.",
            "What did the janitor say when he jumped out of the closet?" "Supplies!",
            "Have you heard about the chocolate record player? It sounds pretty sweet.",
            "What did the ocean say to the beach?" "Nothing, it just waved.",
            "Why do seagulls fly over the ocean?" "Because if they flew over the bay, we\'d call them bagels.",
            "I only know 25 letters of the alphabet. I don\'t know y.",
            "How does the moon cut his hair?" "Eclipse it.",
            "What did one wall say to the other?" "I\'ll meet you at the corner.",
            "What did the zero say to the eight?" "That belt looks good on you.",
            "A skeleton walks into a bar and says, \'Hey, bartender. I\'ll have one beer and a mop.\'",
            "Where do fruits go on vacation?" "Pear-is!",
            "I asked my dog what\'s two minus two. He said nothing.",
            "What did Baby Corn say to Mama Corn?" "Where\'s Pop Corn?",
            "What\'s the best thing about Switzerland?" "I don\'t know, but the flag is a big plus.",
            "What does a sprinter eat before a race?" "Nothing, they fast!",
            "Where do you learn to make a banana split?" "Sundae school.",
            "What has more letters than the alphabet?" "The post office!",
            "Dad, did you get a haircut?" "No, I got them all cut!",
            "What do you call a poor Santa Claus?" "St. Nickel-less.",
            "I got carded at a liquor store, and my Blockbuster card accidentally fell out. The cashier said never mind.",
            "Where do boats go when they\'re sick? To the boat doc.",
            "I don\'t trust those trees. They seem kind of shady.",
            "My wife is really mad at the fact that I have no sense of direction. So I packed up my stuff and right!",
            "How do you get a squirrel to like you? Act like a nut.",
            "Why don\'t eggs tell jokes? They\'d crack each other up.",
            "I don\'t trust stairs. They\'re always up to something.",
            "What do you call someone with no body and no nose? Nobody knows.",
            "Did you hear the rumor about butter? Well, I\'m not going to spread it!",
            "Why couldn\'t the bicycle stand up by itself? It was two tired.",
            "What did one hat say to the other?" "Stay here! I\'m going on ahead.",
            "Why did Billy get fired from the banana factory? He kept throwing away the bent ones.",
            "Dad, can you put my shoes on?" "No, I don\'t think they\'ll fit me.",
            "Why can\'t a nose be 12 inches long? Because then it would be a foot.",
            "What does a lemon say when it answers the phone?" "Yellow!",
            "This graveyard looks overcrowded. People must be dying to get in.",
            "What kind of car does an egg drive?" "A yolkswagen.",
            "Dad, can you put the cat out?" "I didn\'t know it was on fire.",
            "How do you make 7 even?" "Take away the s.",
            "How does a taco say grace?" "Lettuce pray.",
            "What time did the man go to the dentist? Tooth hurt-y.",
            "Why didn\'t the skeleton climb the mountain?" "It didn\'t have the guts.",
            "What do you call it when a snowman throws a tantrum?" "A meltdown.",
            "How many tickles does it take to make an octopus laugh? Ten tickles.",
            "I have a joke about chemistry, but I don\'t think it will get a reaction.",
            "What concert costs just 45 cents? 50 Cent featuring Nickelback!",
            "What does a bee use to brush its hair?" "A honeycomb!",
            "How do you make a tissue dance? You put a little boogie in it.",
            "Why did the math book look so sad? Because of all of its problems!",
            "What do you call cheese that isn\'t yours? Nacho cheese.",
            "My dad told me a joke about boxing. I guess I missed the punch line.",
            "What kind of shoes do ninjas wear? Sneakers!",
            "How does a penguin build its house? Igloos it together.",
            "How did Harry Potter get down the hill?" "Walking. JK! Rowling.",
            "I used to be addicted to soap, but I\'m clean now.",
            "A guy walks into a bar... and he was disqualified from the limbo contest.",
            "You think swimming with sharks is expensive? Swimming with sharks cost me an arm and a leg.",
            "When two vegans get in an argument, is it still called a beef?",
            "I ordered a chicken and an egg from Amazon. I\'ll let you know...",
            "Do you wanna box for your leftovers?" "No, but I\'ll wrestle you for them.",
            "That car looks nice but the muffler seems exhausted.",
            "Shout out to my fingers. I can count on all of them.",
            "If a child refuses to nap, are they guilty of resisting a rest?",
            "What country\'s capital is growing the fastest?" "Ireland. Every day it\'s Dublin.",
            "I once had a dream I was floating in an ocean of orange soda. It was more of a fanta sea.",
            "Did you know corduroy pillows are in style? They\'re making headlines.",
            "Did you hear about the kidnapping at school? It\'s okay, he woke up.",
            "A cheeseburger walks into a bar. The bartender says, \'Sorry, we don\'t serve food here.\'",
            "I once got fired from a canned juice company. Apparently I couldn\'t concentrate.",
            "I used to play piano by ear. Now I use my hands.",
            "Have you ever tried to catch a fog? I tried yesterday but I mist.",
            "I\'m on a seafood diet. I see food and I eat it.",
            "Why did the scarecrow win an award? Because he was outstanding in his field.",
            "I made a pencil with two erasers. It was pointless.",
            "How do you make a Kleenex dance? Put a little boogie in it!",
            "I\'m reading a book about anti-gravity. It\'s impossible to put down!",
            "Did you hear about the guy who invented the knock-knock joke? He won the \'no-bell\' prize.",
            "I\'ve got a great joke about construction, but I\'m still working on it.",
            "I used to hate facial hair...but then it grew on me.",
            "I decided to sell my vacuum cleaner—it was just gathering dust!",
            "I had a neck brace fitted years ago and I\'ve never looked back since.",
            "You know, people say they pick their nose, but I feel like I was just born with mine.",
            "What\'s brown and sticky? A stick.",
            "Why can\'t you hear a psychiatrist using the bathroom? Because the \'P\' is silent.",
            "What do you call an elephant that doesn\'t matter? An irrelephant.",
            "What do you get from a pampered cow? Spoiled milk.",
            "I like telling Dad jokes. Sometimes he laughs!",
            "What\'s the best smelling insect?" "A deodor-ant.",
            "I used to be a personal trainer. Then I gave my too weak notice.",
            "Did I tell you the time I fell in love during a backflip? I was heels over head!",
            "If a child refuses to sleep during nap time, are they guilty of resisting a rest?",
            "I ordered a chicken and an egg online. I’ll let you know.",
            "It takes guts to be an organ donor.",
            "If you see a crime at an Apple Store, does that make you an iWitness?",
            "I\'m so good at sleeping, I can do it with my eyes closed!",
            "I was going to tell a time-traveling joke, but you guys didn\'t like it.",
            "What did the vet say to the cat?" "How are you feline?",
            "What do you call a lazy baby kangaroo?" "A pouch potato!",
            "What happens when M&M’s can’t agree on anything?" "They reach an M-passe.",
            "What do you call a fake noodle?" "An impasta.",
            "What do you call a belt made of watches?" "A waist of time.",
            "What happens when a strawberry gets run over crossing the street?" "Traffic jam.",
            "What do you call two monkeys that share an Amazon account?" "Prime mates.",
            "What do you call a pony with a sore throat?" "A little hoarse.",
            "Where do math teachers go on vacation?" "Times Square.",
            "Whenever I try to eat healthy, a chocolate bar looks at me and Snickers.",
            "What does garlic do when it gets hot?" "It takes its cloves off.",
            "What\'s a robot\'s favorite snack?" "Computer chips.",
            "How much does it cost Santa to park his sleigh?" "Nothing, it\'s on the house.",
            "Mountains aren\'t just funny. They\'re hill areas.",
            "What do clouds wear?" "Thunderwear.",
            "Why are piggy banks so wise?" "They\'re filled with common cents.",
            "Why is Peter Pan always flying?" "He neverlands.",
            "How do you get a good price on a sled?" "You have toboggan.",
            "How can you tell if a tree is a dogwood tree?" "By its bark.",
            "I used to hate facial hair, but then it grew on me.",
            "It\'s inappropriate to make a \'dad joke\' if you\'re not a dad. It\'s a faux pa.",
            "What do you call a hot dog on wheels?" "Fast food!",
            "Where do young trees go to learn?" "Elementree school.",
            "Did you hear about the circus fire? It was in tents.",
            "Can February March? No, but April May!",
            "How do lawyers say goodbye? We\'ll be suing ya!",
            "Wanna hear a joke about paper? Never mind—it\'s tearable.",
            "What\'s the best way to watch a fly fishing tournament? Live stream.",
            "Spring is here! I got so excited I wet my plants.",
            "I could tell a joke about pizza, but it\'s a little cheesy.",
            "Don\'t trust atoms. They make up everything!",
            "When does a joke become a dad joke? When it becomes apparent.",
            "I wouldn\'t buy anything with velcro. It\'s a total rip-off.",
            "What’s an astronaut’s favorite part of a computer? The space bar.",
            "I don\'t play soccer because I enjoy the sport. I\'m just doing it for kicks!",
            "Why are elevator jokes so classic and good? They work on many levels.",
            "Why do bees have sticky hair? Because they use a honeycomb.",
            "Which state has the most streets? Rhode Island.",
            "What did the coffee report to the police? A mugging.",
            "What did the fish say when he hit the wall? Dam.",
            "Is this pool safe for diving? It deep ends.",
            "If you see a crime happen at the Apple store, what does it make you? An iWitness.",
        )
        self.UWUPROMPT = {
            "uwu",
            "owo"
        }
        self.UWUROAST = (
            "Average 42 yo man with anime pfp be like",
            "Where do you think you are, an e-girl server?",
            "You’re entitled to your incorrect opinion",
            "My middle finger gets a boner every time I see you",
            "Is there an app I can download to make you disappear?",
            "Stop using uwu, you furry!",
            "It’s scary to think people like you are allowed to vote",
            "I miss the golden days when the UWU word was banned."
        )
        self.helpMsg = """
__**Prefixes**__ = `athena `, `hey athena `, `hi athena `, `hello athena `, 
`sup athena `, `athena senpai `, `$`, `?`, and mentions.

__**Command List**__:
1. `ping` - Pings Athena
2. `help` - Shows this message
3. `roll a dice` - Rolls a dice
4. `magic 8 ball` - Ask Athena a question
5. `tell me a joke` or `tell me a dad joke` - Ask Athena a dad joke
6. `check resources` - Check memory and thread usage
7. `i am bored` - Get a random activity
8. `what is {x}` or `google {x}` - Get google results. *eg*: `what is the meaning of life`
9. `search for {x} on wikipedia` - Get wikipedia results. *eg*: `search for the meaning of life on wikipedia`
10. `define {x}` - Get dictionary results. *eg*: `define the meaning of life`
11. `download {x}` - Download youtube videos. *eg*: `download https://www.youtube.com/watch?v=meaningoflife`
12. `nasa` - Get NASA photo
13. `agify {x}` - Get age from single-worded name. *eg*: `agify Doctor`
14. `dog` - Get a random dog picture. *eg*: `dog`
15. `cat` - Get a random cat picture. *eg*: `cat`
16. `cocktail random` or `cocktail {x}` - Get a random cocktail or look for one (WIP)
17. `fact` - Get a random fact
18. `bucket list` - Get a random bucket list item
19. `rhyme {x}` - To find a word that rhymes with another word. *eg*: `rhyme life`
20. `reddit {x}` - Get a random reddit post from valid subreddit. *eg*: `reddit cute`
Valid subreddits are: `cute`, `naturegifs`, `wholesomememes`, `animalsbeingbros`, `aww`

__**Music**__:
1. `join` - Join a voice channel
2. `add {x}` - Add a song to the queue
3. `play` - Play or starts the music playback
4. `pause` - Pauses the music
5. `resume` - Resumes the music
6. `stop` - Stops the music
7. `queue` - Shows the queue
8. `skip` - Skips the current song
9. `loop` - Loops the current queue
10. `shuffle` - Shuffles the current queue
11. `remove {x}` - Removes a song from the queue. `x` is the index of the song you'd get from `queue`.

If you face any bugs, use `/feedback` to report it please. 😊
"""

    def greeting_method(self):
        return random.choice(self.GREETINGRESPONSE)

    def magic8ball_method(self):
        return random.choice(self.MAGIC8BALL)

    def dad_joke_method(self):
        return random.choice(self.DADJOKE)

    def uwu_roast_method(self):
        return random.choice(self.UWUROAST)

    def roll_dice_method(self):
        return random.randint(1, 6)

    def bored(self):
        response = requests.get("https://www.boredapi.com/api/activity/").json()
        return response["activity"]

    def agify(self):
        def random_age(firstLow, FirstHigh, secondLow, secondHigh, k):
            if random.random() < k:
                randNumber = random.randint(firstLow, FirstHigh)
            else:
                randNumber = random.randint(secondLow, secondHigh)
            return randNumber
        return random_age(2, 60, 61, 500, 0.8)

    def dog(self):
        response = requests.get("https://dog.ceo/api/breeds/image/random").json()
        return response["message"]

    def cat(self):
        response = requests.get("https://api.thecatapi.com/v1/images/search").json()
        return response[0]["url"]

    def random_cocktail(self):
        #? https://api-ninjas.com/api/cocktail
        response = requests.get("https://www.thecocktaildb.com/api/json/v1/1/random.php").json()
        return response["drinks"][0]["strDrink"]

    def search_cocktail(self, name):
        response = requests.get(f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={name}").json()
        return response["drinks"][0]["strInstructions"]

    def fact(self, apiKey):
        api_url = "https://api.api-ninjas.com/v1/facts"
        response = requests.get(api_url, headers={'X-Api-Key': apiKey}).json()
        return response[0]["fact"]

    def bucket_list(self, apiKey):
        api_url = "https://api.api-ninjas.com/v1/bucketlist"
        response = requests.get(api_url, headers={'X-Api-Key': apiKey}).json()
        return response["item"]

    def rhyme(self, apiKey, word):
        api_url = f"https://api.api-ninjas.com/v1/rhyme?word={word}"
        response = requests.get(api_url, headers={'X-Api-Key': apiKey}).json()
        return ", ".join(response)