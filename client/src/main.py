import task_runner
import os
import requests

    
def main(): 
    while True:
        task = get_next_task()
                
        if not task:
            break
        
        task_runner.run_task(task)
        
        import time
        time.sleep(5)

def get_next_task():
    api_url = os.getenv("SERVER_API_URL")
    allowed_scripts = os.listdir("/app/scripts")
        
    return requests.post(f"{api_url}/tasks/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

if __name__ == "__main__":
    main()
