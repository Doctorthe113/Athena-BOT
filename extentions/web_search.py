from unittest import result
import wikipedia
import requests
from googleapiclient.discovery import build

#! all the queries are case sensitive
class webSearch():
    def __init__(self, apiKey, cseId) -> None:
        self.APIKEY = apiKey
        self.CSEID = cseId
        self.dictionaryApi = "https://api.dictionaryapi.dev/api/v2/entries/en/"


    def google_search(self, query):
        service = build("customsearch", "v1", developerKey=self.APIKEY, static_discovery=False).cse()
        result = service.list(q=query, cx=self.CSEID, safe="high").execute()
        searchResult = ""
        for i in range(0, 6):
            searchResult += "\n""- " + result["items"][i]["snippet"] + "\n" + "<" + result["items"][i]["link"] + ">"
        return searchResult


    def wikiSearch(self, query):
        relatedArticles = wikipedia.search(query)
        try:
            wikiSummary = wikipedia.summary(query, chars=2000, auto_suggest=False, redirect=True)
        except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError) as e:
            wikiSummary = e
        return wikiSummary, relatedArticles


    def dictionary(self, query):
        vocub = requests.get(self.dictionaryApi + query).json()
        word = vocub[0]["word"]
        pronounciation = vocub[0]["phonetics"][0].get("audio", "unknown")
        phonetics = vocub[0]["phonetics"][1].get("text", "unknown")
        origin = vocub[0].get("origin", "unknown")
        meanings = vocub[0]["meanings"]
        definition = ""
        for i in meanings:
            definition += "\n" + "**" + i["definitions"][0]["definition"] + \
                        "**" + "\n" + i["partOfSpeech"]
        return word, phonetics, pronounciation, origin, definition