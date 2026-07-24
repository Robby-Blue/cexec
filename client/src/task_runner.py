import docker_helper as docker
import paths
import json
import os
import hashlib
import api

def run_task(task):              
    id = task["id"]
    script = task["script"]
    
    print(f"> start task #{id}")
    
    make_env()
    download_files(task.get("files", []))
    
    exit_code, log = docker.run_script_container(script)
    
    print(f"< task finished: {exit_code}")
    
    complete_run(id, exit_code, log)

def download_files(file_paths):
    for path in file_paths:
        info = api.get(f"/files/info/{path}").json()

        if info["type"] == "file":
            download_file(path)
        elif info["type"] == "folder":
            child_paths = []
            for child_name in info["children"]:
                child_path = os.path.join(path, child_name)
                child_paths.append(child_path)
                
            download_files(child_paths)

def download_file(path):
    fs_path = os.path.join(paths.RUNNER_INPUT, path)
    fs_parent = os.path.dirname(fs_path)
    os.makedirs(fs_parent, exist_ok=True)
    
    r = api.get(f"/files/download/{path}")
    content = r.content
    
    with open(fs_path, "wb") as f:
        f.write(content)

def complete_run(id, exit_code, log):
    if os.path.exists(paths.RUNNER_OUTPUT_JSON):
        with open(paths.RUNNER_OUTPUT_JSON, "r") as f:
            output_data = json.load(f)
    else:
        output_data = {}

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