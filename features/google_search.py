from json import load
from googleapiclient.discovery import build

with open("./keys.json") as f:
    keys = load(f)
    api_key = keys["google_api_key"]
    cse_id = keys["search_engine_id"]

def google_search(search_term):
    service = build("customsearch", "v1", developerKey = api_key, static_discovery = False).cse()
    res = service.list(q = search_term, cx = cse_id, safe = "high").execute()

    snippet = ""
    for index in range(0, 6):
        snippet += "\n""- " + res["items"][index]["snippet"] + "\n" + "<" + res["items"][index]["link"] + ">"

    return snippet