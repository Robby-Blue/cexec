import task_runner
import paths
import os
import requests

def main(): 
    while True:
        task = get_next_task()
                
        if not task:
            break
        
        task_runner.run_task(task)

def get_next_task():
    api_url = os.getenv("SERVER_API_URL")
    allowed_scripts = os.listdir(paths.RUNNER_SCRIPTS)
        
    return requests.post(f"{api_url}/tasks/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

if __name__ == "__main__":
    main()
