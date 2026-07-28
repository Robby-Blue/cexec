import requests
import os

api_url = os.getenv("SERVER_API_URL")
auth_key = os.getenv("AUTH_KEY")

def get(url, **kwargs):
    return requests.get(f"{api_url}{url}", headers = {
        "Authorization": f"Bearer {auth_key}"
    }, **kwargs)

def post(url, **kwargs):
    return requests.post(f"{api_url}{url}", headers = {
        "Authorization": f"Bearer {auth_key}"
    }, **kwargs)