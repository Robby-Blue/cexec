import json

with open("config.json") as f:
    data = json.load(f)

scheduled_tasks = data["scheduled_tasks"]
priorities = data["priorities"]

def priority_from_str(priority_str):
    print(priority_str, priorities)
    if priority_str not in priorities:
        return 0
    return priorities.index(priority_str)

def get_priority_str(priority):
    if  priority >= len(priorities):
        return priorities(len(priorities) - 1)
    return priorities[priority]