import json
import os
import hmac

import files

def read_auth_key_perm(perm_data):
    if isinstance(perm_data, str):
        return {
            "type": perm_data
        }
        
    if "path" in perm_data:
        perm_data["path"] = files.safe_get_file_path(perm_data["path"])
    
    return perm_data

def read_auth_keys(auth_key_data):
    auth_keys = []
    for auth_key in auth_key_data:
        auth_key_name = auth_key["name"]
        key = os.environ[auth_key_name]
        
        if not auth_key:
            continue
        auth_key["key"] = key
        auth_key["permissions"] = [
            read_auth_key_perm(perm) for perm in
            auth_key["permissions"]
        ]
        
        auth_keys.append(auth_key)
    
    return auth_keys

with open("config.json") as f:
    data = json.load(f)

scheduled_tasks = data["scheduled_tasks"]
priorities = data["priorities"]
auth_keys = read_auth_keys(data["auth_keys"])

def get_perms_for_key(used_auth_key):
    for auth_key in auth_keys:
        if not hmac.compare_digest(used_auth_key, auth_key["key"]):
            continue
        return auth_key["permissions"]
    return []

def has_perms_for_key(req_perm, used_auth_key):
    perms = get_perms_for_key(used_auth_key)
    for perm in perms:
        if perm["type"] == req_perm:
            return True
    return False

def priority_from_str(priority_str):
    if priority_str not in priorities:
        return 0
    return priorities.index(priority_str)

def get_priority_str(priority):
    if  priority >= len(priorities):
        return priorities(len(priorities) - 1)
    return priorities[priority]