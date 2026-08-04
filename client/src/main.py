import task_runner
import paths
import os
import api
import json
import time

with open("config.json") as f:
    config = json.load(f)

auto_exit = config.get("auto_exit", True)

def main():
    with open("version.json") as f:
        version_id = json.load(f)["version_id"]
    
    while True:
        check_version(version_id)
        task = get_next_task()
        
        if not task["found"]:
            if auto_exit:
                return
            else:
                time.sleep(60 * 60)
                continue
        
        task_runner.run_task(task)

def check_version(client_version_id):
    server_version_id = api.get("/version").json()["version_id"]
    
    if client_version_id != server_version_id:
        print("version mismatch")
        print(f"{client_version_id=}, {server_version_id=}")
        exit(1)
    
def get_next_task():
    allowed_scripts = os.listdir(paths.RUNNER_SCRIPTS)
        
    return api.post("/tasks/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

if __name__ == "__main__":
    main()
