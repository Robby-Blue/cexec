import task_runner
import paths
import os
import api

def main(): 
    while True:
        task = get_next_task()
        
        if not task["found"]:
            break
        
        task_runner.run_task(task)

def get_next_task():
    allowed_scripts = os.listdir(paths.RUNNER_SCRIPTS)
        
    return api.post("/tasks/next", json={
        "allowed_scripts": allowed_scripts
    }).json()

if __name__ == "__main__":
    main()
