import requests
import os

api_url = os.getenv("SERVER_API_URL")

def get(url, **kwargs):
    return requests.get(f"{api_url}{url}", **kwargs)

def post(url, **kwargs):
    return requests.post(f"{api_url}{url}", **kwargs)