import requests

dictionary_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def dictionary(keyword):
    result = requests.get(dictionary_url + keyword).json()

    word = result[0]["word"]
    try:
        pronounciation = result[0]["phonetics"][0]["audio"]
    except: pronounciation = "Unknown"
    try:
        phonetics = result[0]["phonetics"][1]["text"]
    except: phonetics = "Unknown"
    origin = result[0].get("origin", "unknown")
    meanings = result[0]["meanings"]

    definition = ""
    for meaning in meanings:
        definition += "\n" + "**" + meaning["definitions"][0]["definition"] + "**" + "\n" + meaning["partOfSpeech"]

    result = f"""## {word}
### {phonetics}
__Pronounciation__: {pronounciation}
__Origin__: {origin}
__Definitions__: {definition}"""

    return result
