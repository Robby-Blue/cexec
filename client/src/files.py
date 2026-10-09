import api

import os
import paths

def create_backup():
    print(">>>")
    print("Creating backup")
    
    server_files = api.get("/files/backup_info").json()
    changed_files = get_changed_files(server_files)
    print(f"Files Count: {len(changed_files)}")
    
    byte_count = 0
    for file_data in changed_files:
        byte_count += file_data["file_size_bytes"]
    
    print(f"Files Size:  {format_byte_count(byte_count)}")
    
    for file_data in changed_files:
        backup_file(file_data["path"])
    
    print("<<<")
    print("Goodbye")
    
def backup_file(server_path):
    fs_path = os.path.join(paths.RUNNER_BACKUP, server_path)

    r = api.get(f"/files/download/{server_path}")
    content = r.content

    fs_parent = os.path.dirname(fs_path)
    os.makedirs(fs_parent, exist_ok=True)

    with open(fs_path, "wb") as f:
        f.write(content) 

def get_changed_files(files):
    def should_download_file(fs_path, data):
        if not os.path.exists(fs_path):
            return True
        stat = os.stat(fs_path)
        server_file_edited = data["last_edit_time_unix"] > stat.st_mtime
        files_different_size = data["file_size_bytes"] > stat.st_size
        return server_file_edited or files_different_size
    
    changed_files = []
    for server_file_data in files:
        fs_path = os.path.join(paths.RUNNER_BACKUP, server_file_data["path"])
        if should_download_file(fs_path, server_file_data):
            changed_files.append(server_file_data)
    
    return changed_files

def format_byte_count(n):
    kb = 1024
    mb = 1024 * 1024
    
    if n < kb:
        return f"{n} bytes"
    if n < mb:
        return f"{n / kb:.1f} KB"
    return f"{n / mb:.1f} MB"