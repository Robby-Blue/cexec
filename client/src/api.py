import requests
import os

api_url = os.getenv("SERVER_API_URL")
auth_key = os.getenv("AUTH_KEY")

def get(url, **kwargs):
    r = requests.get(f"{api_url}{url}", headers = {
        "Authorization": f"Bearer {auth_key}"
    }, **kwargs)
    exit_on_error(r)
    return r

def post(url, **kwargs):
    r = requests.post(f"{api_url}{url}", headers = {
        "Authorization": f"Bearer {auth_key}"
    }, **kwargs)
    exit_on_error(r)
    return r

def exit_on_error(r):
    if r.status_code == 200:
        return
    print("<<<")
    print(r.status_code)
    print(r.text)
    exit(1)