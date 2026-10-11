import docker_helper as docker
import paths
import api

from files import format_byte_count
import shutil
import os
import json

def run_task(task):              
    id = task["id"]
    script = task["script"]
    
    print(">>>")
    print(f"Id:     #{id}")
    print(f"Script: {script}")
    print(f"Tag:    {task["tag"]}")
    print(">>>")
    
    make_env()
    download_files(task.get("input_files", []))
    write_vars(task.get("vars", {}))
    
    exit_code, log = docker.run_script_container(script)
    
    print("<<<")
    print(f"Exit Code: {exit_code}")
    print(f"Log:       {len(log.split("\n"))} lines")
    
    complete_run(task, exit_code, log)

def write_vars(vars):
    with open(paths.RUNNER_VARS, "w") as f:
        json.dump(vars, f)

def download_files(file_paths):
    for paths_data in file_paths:
        server_path = paths_data["server"]
        client_path = paths_data["client"]
        
        info = api.get(f"/files/info/{server_path}").json()

        if not info:
            continue

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

    run_files = find_files("run", paths.RUNNER_OUTPUT_RUN)
    global_files = find_files("global", paths.RUNNER_OUTPUT_GLOBAL)

    files = [*run_files, *global_files]
    
    print(f"Files:     {len(files)}")

    files.append({
        "metadata": {
            "type": "run",
            "path": "log",
            "path_relative_to_type": "log",
            "byte_count": len(log.encode("utf-8"))
        },
        "content": ("files", ("log", log, "text/plain"))
    })
    byte_count = sum([file["metadata"]["byte_count"] for file in files])
    print(f"Size:      {format_byte_count(byte_count)}")
    
    upload_files(id, files)
    
    complete_files = []
    
    included_file = get_included_file(output_data, files)
    if included_file:
        included_file_content, included_file_path, included_file_name = included_file
        output_data["webhook"]["include_file"] = {
            "path": included_file_path,
            "name": included_file_name,
        }
        complete_files.append(("included_file", ("included", included_file_content, "application/octet-stream")))
    
    complete_files.append(("log_file", ("log", log, "text/plain")))
    
    data = {
        "id": str(id),
        "exit_code": exit_code,
        "output": output_data,
        "files_count": len(files)
    }
    complete_files.append(("data", ("data", json.dumps(data))))
    
    return api.post(f"/runs/complete",
        files=complete_files
    ).json()

def get_included_file(output_data, files):
    included_file = output_data.get("webhook", {}).get("include_file", {})
    if not included_file:
        return None
    
    if isinstance(included_file, str):
        file_path = included_file
        file_name = os.path.basename(file_path)
    elif isinstance(included_file, dict):
        file_path = included_file["path"]
        file_name = included_file["name"]
    else:
        return None

    file = [file for file in files
        if file["metadata"]["path"] == file_path][0]
    
    return file["content"][1][1], file_path, file_name

def upload_files(id, files):
    parts = split_files(files)
    
    for part in parts:
        data = {
           "id": id,
            "metadata_list": [file["metadata"] for file in part]
        }
        part_files = [file["content"] for file in part]
        
        files = [
            ("data", ("data", json.dumps(data), "application/json")),
            *part_files
        ]
        
        api.post(f"/runs/upload_files",
            files=files,
        ).json()

def split_files(files):
    parts = []
    part = []
    
    mb_size = 1024*1024
    max_size = mb_size*1024
    
    part_size = 0
    part_len = 0
    for file in files:
        part_len += 1
        part_size += file["metadata"]["byte_count"]
        
        if part_size > max_size or part_len == 1000:
            parts.append(part)
            part = []

        part.append(file)
    
    if part:
        parts.append(part)

    return parts

def map_output_files(maps):
    for map in maps:
        src = os.path.join(paths.RUNNER_OUTPUT, map["client"])
        dest = os.path.join(paths.RUNNER_OUTPUT, map["server"])
        
        if not os.path.exists(src):
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy(src, dest)

def find_files(type, path):
    files = []
    
    for file_name in os.listdir(path):
        if file_name.startswith("."):
            continue
        
        file_path = os.path.join(path, file_name)
        if os.path.isdir(file_path):
            new_files = find_files(type, file_path)
            files.extend(new_files)
        else:
            entry, new_file = process_file(type, file_path)
            files.append({
                "metadata": entry,
                "content": new_file
            })
    
    return files

def process_file(type, path):
    rel = os.path.relpath(path, f"/app/workspace/output/")
    rel_type = os.path.relpath(path, f"/app/workspace/output/{type}")
    
    with open(path, "rb") as f:
        data = f.read()
        
    entry = {
        "type": type,
        "path": rel,
        "path_relative_to_type": rel_type,
        "byte_count": len(data)
    }
    
    file = ("files", (rel, data))
    
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