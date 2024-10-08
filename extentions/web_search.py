import wikipedia
import urllib3
import requests
import praw  # ? use the async version of praw?
import random
from googleapiclient.discovery import build

urllib3.disable_warnings()


#! all the queries are case sensitive
class WebSearch:
    def __init__(self, apiKey, cseId) -> None:
        self.APIKEY = apiKey
        self.CSEID = cseId
        self.dictionaryApi = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.descoApi = "https://prepaid.desco.org.bd/api/tkdes/customer/getBalance?"

    def desco_bill(self, meter, account):
        response = requests.get(
            self.descoApi, params={"accountNo": account, "meterNo": meter}, verify=False
        ).json()
        balance = response["data"]["balance"]
        return balance

    def google_search(self, query):
        service = build(
            "customsearch", "v1", developerKey=self.APIKEY, static_discovery=False
        ).cse()
        result = service.list(q=query, cx=self.CSEID, safe="high").execute()
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

    def wikiSearch(self, query):
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

    def dictionary(self, query):
        vocub = requests.get(self.dictionaryApi + query).json()
        word = vocub[0]["word"]
        pronounciation = vocub[0]["phonetics"][0].get("audio", "unknown")
        phonetics = vocub[0]["phonetics"][0].get("text", "unknown")
        origin = vocub[0].get("origin", "unknown")
        meanings = vocub[0]["meanings"]
        definition = ""
        for i in meanings:
            definition += (
                "\n"
                + "**"
                + i["definitions"][0]["definition"]
                + "**"
                + "\n"
                + i["partOfSpeech"]
            )
        return word, phonetics, pronounciation, origin, definition

    def reddit(self, clientID, clientSecret, subreddit):
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
