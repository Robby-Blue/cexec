import docker_helper as docker
import paths
import requests
import json
import os
import hashlib

def run_task(task):              
    id = task["id"]
    script = task["script"]
    
    make_env()
    
    exit_code, log = docker.run_script_container(script)

    complete_run(id, exit_code, log)

def complete_run(id, exit_code, log):
    if os.path.exists(paths.RUNNER_OUTPUT_JSON):
        with open(paths.RUNNER_OUTPUT_JSON, "r") as f:
            output_data = json.load(f)
    else:
        output_data = {}
    
    api_url = os.getenv("SERVER_API_URL")

    run_files_list, run_files = find_files("run", paths.RUNNER_OUTPUT_RUN)
    global_files_list, global_files = find_files("global", paths.RUNNER_OUTPUT_GLOBAL)

    files_list = [*run_files_list, *global_files_list]
    files = [*run_files, *global_files]

    files_list.append({
        "type": "run",
        "path": "log",
        "name": "log"
    })
    
    data = {
        "id": str(id),
        "exit_code": exit_code,
        "output": output_data,
        "files_list": files_list
    }

    files.append(("data", ("data", json.dumps(data), "application/json")))
    files.append(("files", ("log", log, "text/plain")))

    return requests.post(f"{api_url}/runs/complete",
        files=files
    ).json()

def find_files(type, path):
    files_list = []
    files = []
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            new_list, new_files = find_files(type, file_path)
            files_list.extend(new_list)
            files.extend(new_files)
        else:
            entry, new_file = process_file(type, file_path)
            files_list.append(entry)
            files.append(new_file)
    
    return files_list, files

def process_file(type, path):
    path_md5 = hashlib.md5(path.encode()).hexdigest()
    
    rel = os.path.relpath(path, f"/app/workspace/output/{type}")

    entry = {
        "type": type,
        "path": rel,
        "name": path_md5
    }
    
    with open(path, "rb") as f:
        data = f.read()
    file = ("files", (path_md5, data))
    
    return entry, file

def make_env():
    del_dir(paths.RUNNER_OUTPUT)
    os.makedirs(paths.RUNNER_OUTPUT, exist_ok=True)
    os.makedirs(paths.RUNNER_OUTPUT_RUN, exist_ok=True)
    os.makedirs(paths.RUNNER_OUTPUT_GLOBAL, exist_ok=True)

def del_dir(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            del_dir(file_path)
        else:
            os.remove(file_path)
    os.rmdir(path)