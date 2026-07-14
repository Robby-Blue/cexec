import docker_helper as docker
import requests
import json
import os

def run_task(task):              
    id = task["id"]
    script = task["script"]
        
    exit_code, log = docker.run_script_container(script)
        
    print(complete_run(id, exit_code, log))

def complete_run(id, exit_code, log):
    with open("/app/workspace/output/output.json", "r") as f:
        output_data = json.load(f)
    
    api_url = os.getenv("SERVER_API_URL")
    
    # files = [
    #     ("log", ("log", log, "text/plain")),
    # ]
    
    data = {
        "id": str(id),
        "exit_code": exit_code,
        "output": output_data
    }
    
    return requests.post(f"{api_url}/runs/complete",
        json=data,
        # files=files
    ).json()