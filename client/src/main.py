import docker_helper as docker
import os
import requests

api_url = os.getenv("SERVER_API_URL")
    
def main(): 
    while True:
        task = get_next_task()
                
        if not task:
            break
                
        id = task["id"]
        script = task["script"]
        
        docker.run_script_container(script)
        
        mark_task_completed(id)

def get_next_task():
    allowed_scripts = os.listdir("/app/scripts")
        
    return requests.post(f"{api_url}/tasks/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

def mark_task_completed(id):    
    return requests.post(f"{api_url}/tasks/mark_completed", json={
        "id": str(id)
    }).json()

if __name__ == "__main__":
    main()
