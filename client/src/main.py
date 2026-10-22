import runner
import files
import api

import paths
import os
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
        task = get_next_run()
        
        if not task["found"]:
            if auto_exit:
                break
            else:
                time.sleep(60 * 60)
                continue
        
        runner.execute_run(task)
    
    files.create_backup()

def check_version(client_version_id):
    server_version_id = api.get("/version").json()["version_id"]
    
    if client_version_id != server_version_id:
        print("version mismatch")
        print(f"{client_version_id=}, {server_version_id=}")
        exit(1)
    
def get_next_run():
    allowed_scripts = os.listdir(paths.RUNNER_SCRIPTS)
        
    return api.post("/runs/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

if __name__ == "__main__":
    main()
