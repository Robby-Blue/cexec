import json
import os

import files

with open("config.json") as f:
    data = json.load(f)

scheduled_tasks = data["scheduled_tasks"]
priorities = data["priorities"]
file_perms = []
for file_perm in data["file_perms"]:
    auth_key_name = file_perm["auth_key_name"]
    auth_key = os.environ[auth_key_name]
    
    if not auth_key:
        continue
    file_perm["auth_key"] = auth_key
    
    file_perm["path"] = files.safe_get_file_path(file_perm["path"])
    file_perms.append(file_perm)

def priority_from_str(priority_str):
    if priority_str not in priorities:
        return 0
    return priorities.index(priority_str)

def get_priority_str(priority):
    if  priority >= len(priorities):
        return priorities(len(priorities) - 1)
    return priorities[priority]