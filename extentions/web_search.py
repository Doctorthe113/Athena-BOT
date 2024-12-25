import wikipedia
import urllib3
import requests
import praw  # ? use the async version of praw?
import random
import re
import bs4
from googleapiclient.discovery import build

urllib3.disable_warnings()


#! all the queries are case sensitive
class Web_Search:
    def __init__(self, apiKey, cseId) -> None:
        self.APIKEY = apiKey
        self.CSEID = cseId
        # self.dictionaryApi = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.descoApi = "https://prepaid.desco.org.bd/api/tkdes/customer/getBalance?"

    def desco_bill(self, meter, account) -> str:
        response = requests.get(
            self.descoApi, params={"accountNo": account, "meterNo": meter}, verify=False
        ).json()
        balance = response["data"]["balance"]
        return balance

    def google_search(self, query) -> str:
        service = build(
            "customsearch", "v1", developerKey=self.APIKEY, static_discovery=False
        ).cse()
        result = service.list(q=query, cx=self.CSEID, safe="active").execute()
        searchResult = ""

        try:
            for i in range(0, 6):
                searchResult += (
                    "\n"
                    "- "
                    + result["items"][i]["snippet"]
                    + "\n"
                    + "<"
                    + result["items"][i]["link"]
                    + ">"
                )
        except:
            searchResult = "No results found"
        return searchResult

    def wikiSearch(self, query) -> tuple:
        relatedArticles = wikipedia.search(query)
        try:
            wikiSummary = wikipedia.summary(
                query, chars=2000, auto_suggest=False, redirect=True
            )
        except (
            wikipedia.exceptions.DisambiguationError,
            wikipedia.exceptions.PageError,
        ) as e:
            wikiSummary = e
        return wikiSummary, relatedArticles

    def dictionary(self, query) -> tuple:
        # vocub = requests.get(self.dictionaryApi + query).json()
        # word = vocub[0]["word"]
        # pronounciation = vocub[0]["phonetics"][0].get("audio", "unknown")
        # phonetics = vocub[0]["phonetics"][0].get("text", "unknown")
        # origin = vocub[0].get("origin", "unknown")
        # meanings = vocub[0]["meanings"]
        # definition = ""
        # for i in meanings:
        #     definition += (
        #         "\n"
        #         + "**"
        #         + i["definitions"][0]["definition"]
        #         + "**"
        #         + "\n"
        #         + i["partOfSpeech"]
        #     )
        # return word, phonetics, pronounciation, origin, definition
        url = "https://www.merriam-webster.com/dictionary/"
        filteredWord = re.sub(r"[^\w\s]", "", query.lower())
        res = requests.get(url + filteredWord)
        soup = bs4.BeautifulSoup(res.content, "html.parser")

        spellingSuggestion = soup.find("p", class_="spelling-suggestion-text")

        # if the word is not in the free dictionary
        if spellingSuggestion:
            return "Not available in the free dictionary"

        # if the word even exists in the dictionary
        try:
            hword = soup.find("h1").text
            partsOfSpeech = soup.find("h2").text
            defParent = soup.find(class_="vg")
            definition = "\n- ".join(
                [
                    i.text.removeprefix(": ").removesuffix(": such as")
                    for i in defParent.find_all("span", class_="dtText")
                ]
            )
        except AttributeError:
            return "Word not found"

        # for syllables
        try:
            syllables = soup.find("span", class_="word-syllables-entry").text.replace(
                "\u200b", ""
            )
        except AttributeError:
            syllables = "None"

        # for pronounciation
        try:
            audioUrl = soup.find("a", class_="play-pron-v2").get("href")
            audioFilename = re.search(r"file=([^&]+)", audioUrl).group(1)
            firstLetter = audioFilename[0]
            audioStreamUrl = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{firstLetter}/{audioFilename}.mp3"
        except AttributeError:
            audioStreamUrl = "None"

        return {
            "word": hword,
            "partsOfSpeech": partsOfSpeech,
            "definition": definition,
            "syllables": syllables,
            "phonetics": audioStreamUrl,
        }

    def reddit(self, clientID, clientSecret, subreddit) -> str:
        r = praw.Reddit(
            client_id=clientID,
            client_secret=clientSecret,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            check_for_async=False,
        )
        hot_posts = r.subreddit(subreddit).hot(limit=50)
        imgExtensions = ("jpg", "png", "jpeg", "gif")
        postURL = []
        for post in hot_posts:
            if post.media or post.url.endswith(imgExtensions):
                postURL.append(post)
        randomPost = random.choice(postURL)
        if randomPost.url.endswith(imgExtensions):
            return f"https://rxddit.com{randomPost.permalink}"
        else:
            return f"https://embed.works/https://reddit.com{randomPost.permalink}"
