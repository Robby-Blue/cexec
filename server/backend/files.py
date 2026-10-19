import os
import paths
import config

def safe_get_file_path(path):
    fs_path = os.path.join(paths.FILES, path)
    fs_path = os.path.realpath(fs_path)
    if os.path.commonpath([paths.FILES, fs_path]) != paths.FILES:
        return None
    if not os.path.exists(fs_path):
        return None
    return fs_path

def get_permissions(key, req_path):
    req_path = safe_get_file_path(req_path)
    path_perms = []
    
    for perm in config.get_perms_for_key(key):
        if "path" not in perm:
            continue

        file_path = perm["path"]
        if os.path.commonpath([req_path, file_path]) != file_path:
            continue
        
        path_perms.append(perm["type"])
    
    return path_perms

def backup_read_folder(api_path=""):
    files = []
    fs_path = os.path.join(paths.FILES, api_path)
    
    for entry in os.scandir(fs_path):
        file_name = entry.name
        
        api_subpath = os.path.join(api_path, file_name)
        fs_subpath = os.path.join(paths.FILES, fs_path, file_name)
        
        if os.path.isdir(fs_subpath):
            files += backup_read_folder(api_subpath)
        else:
            stat = entry.stat()
            last_edit_time_unix = stat.st_mtime
            file_size_bytes = stat.st_size
            
            files.append({
                "path": api_subpath,
                "last_edit_time_unix": last_edit_time_unix,
                "file_size_bytes": file_size_bytes
            })
    
    return files