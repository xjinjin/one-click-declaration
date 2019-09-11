
import requests
import json

class HttpUtil():

    def __init__(self):
        self.header = {
            'Content-type':'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        }

    def send(self,url,dic):
        response = requests.post(url,data=json.dumps(dic),headers = self.header)
        return response