from urllib import response
import requests

class Nasa:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.photoURL = "https://api.nasa.gov/planetary/apod"

    def getPhoto(self):
        response = requests.get(
                self.photoURL, 
                params={"api_key": self.apiKey}
            ).json()
        photoLink = response["hdurl"]
        return photoLink