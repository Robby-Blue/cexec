import docker_helper as docker
import paths
import api

import hashlib
import shutil
import os
import json

def run_task(task):              
    id = task["id"]
    script = task["script"]
    
    print(f"> start task #{id}")
    
    make_env()
    download_files(task.get("input_files", []))
    
    exit_code, log = docker.run_script_container(script)
    
    print(f"< task finished: {exit_code}")
    
    complete_run(task, exit_code, log)

def download_files(file_paths):
    for paths_data in file_paths:
        server_path = paths_data["server"]
        client_path = paths_data["client"]
        
        info = api.get(f"/files/info/{server_path}").json()

        if info["type"] == "file":
            download_file(server_path, client_path)
        elif info["type"] == "folder":
            child_paths = []
            for child in info["children"]:
                child_name = child["name"]
                child_server_path = os.path.join(server_path, child_name)
                child_client_path = os.path.join(client_path, child_name)
                child_paths.append({
                    "server": child_server_path,
                    "client": child_client_path
                })
                
            download_files(child_paths)

def download_file(server_path, client_path):
    r = api.get(f"/files/download/{server_path}")
    content = r.content
    
    fs_path = os.path.join(paths.RUNNER_INPUT, client_path)
    fs_parent = os.path.dirname(fs_path)
    os.makedirs(fs_parent, exist_ok=True)

    with open(fs_path, "wb") as f:
        f.write(content)

def complete_run(task, exit_code, log):
    id = task["id"]

    if os.path.exists(paths.RUNNER_OUTPUT_JSON):
        with open(paths.RUNNER_OUTPUT_JSON, "r") as f:
            output_data = json.load(f)
    else:
        output_data = {}

    map_output_files(task.get("output_files_map", []))

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

    return api.post(f"/runs/complete",
        files=files
    ).json()

def map_output_files(maps):
    for map in maps:
        src = os.path.join(paths.RUNNER_OUTPUT, map["client"])
        dest = os.path.join(paths.RUNNER_OUTPUT, map["server"])
        
        if not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(src, dest)

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
    del_dir(paths.RUNNER_INPUT)
    os.makedirs(paths.RUNNER_INPUT, exist_ok=True)
    
    del_dir(paths.RUNNER_OUTPUT)
    os.makedirs(paths.RUNNER_OUTPUT, exist_ok=True)
    os.makedirs(paths.RUNNER_OUTPUT_RUN, exist_ok=True)
    os.makedirs(paths.RUNNER_OUTPUT_GLOBAL, exist_ok=True)

def del_dir(path):
    if not os.path.exists(path):
        return
    
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            del_dir(file_path)
        else:
            os.remove(file_path)
    os.rmdir(path)