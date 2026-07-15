import datetime
import requests
import os

def send_webhook(url, embed):
    data = {
        "username": "cexec",
        "embeds": [
            embed
        ]
    }
    
    requests.post(url, json=data)
    
def send_file(url, data):
    requests.post(url, files={"file": data})
    
def get_run_embed(run):
    name = run["script"]
    id = run["task_id"]
    exit_code = run["exit_code"]
    
    if exit_code == 0:
        succeeded_string = "succeeded"
    else:
        succeeded_string = f"failed ({exit_code})"
    
    status_string = f"run #{id} {succeeded_string}"
    
    
    frontend_url = os.getenv("FRONTEND_URL")
    run_url = f"{frontend_url}/runs/{id}"

    timespan = format_timespan(run["completed_at"], run["started_at"])

    return get_template(status_string, run_url, name, [
            {
                "name": "runtime",
                "value": timespan,
                "inline": False
            }
        ]
    )
    
def get_custom_embed(run, data):
    name = run["script"]
    id = run["task_id"]
    
    frontend_url = os.getenv("FRONTEND_URL")
    run_url = f"{frontend_url}/runs/{id}"
    
    fields = data["embeds"][0]["fields"]
    
    return get_template(data["title"], run_url, name, fields)
 
def get_template(title, url, author_name, fields):
    return {
        "title": title,
        "url": url,
        "color": 5793266,
        "author": {
            "name": author_name
        },
        "fields": fields,
        "footer": {
            "text": "cexec report"
        },
        "timestamp": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def format_timespan(dt1, dt2):
    t1 = datetime.datetime.strptime(dt1, "%Y-%m-%d %H:%M:%S")
    t2 = datetime.datetime.strptime(dt2, "%Y-%m-%d %H:%M:%S")
    seconds = abs(int((t2 - t1).total_seconds()))

    units = [
        ("day", 86400),
        ("hour", 3600),
        ("minute", 60),
        ("second", 1),
    ]

    parts = []
    remaining = seconds
    for name, secs in units:
        value, remaining = divmod(remaining, secs)
        if value > 0:
            display_name = name
            if value != 1:
                display_name += "s"
            parts.append(f"{value} {display_name}")
        if len(parts) == 2:
            break

    if len(parts) == 0:
        return "instantly"
    if len(parts) == 1:
        return parts[0]
    return f"{parts[0]} and {parts[1]}"