import db_helper as db
import webhooks
import paths

import os
import json

def get_tasks():
    rows = db.query("SELECT * FROM tasks t LEFT JOIN runs r ON r.task_id = t.id;")
    
    return rows

def create_task(script, data):
    db.exec("""
        INSERT INTO tasks (script)
        VALUES (?);
        """, [script])
    
    id = db.last_row_id()
    data_file_name = f"{id}.json" 
    
    data_file_path = os.path.join(paths.UPCOMING_RUNS, data_file_name)
    with open(data_file_path, "w") as f:
        json.dump(data, f)

def get_next_task(allowed_scripts):
    interpolations = "?," * len(allowed_scripts)
    interpolations = interpolations[:-1]
    
    rows = db.query(f"""
        SELECT t.* FROM tasks t
        LEFT JOIN runs r ON r.task_id = t.id
        WHERE r.started_at IS NULL AND
        script IN ({interpolations});
        """, [*allowed_scripts])

    if len(rows) == 0:
        return None

    row = rows[0]

    return row

def start_run(task_id):
    db.exec("""
        INSERT INTO runs (task_id) VALUES (?);
        """, [task_id])

def complete_run(data, files):
    task_id = data["id"]
    exit_code = data["exit_code"]
    output = data["output"]
    
    db.exec("""
        UPDATE runs SET
        completed_at = CURRENT_TIMESTAMP,
        exit_code = ?
        WHERE task_id = ?;
        """, [exit_code, task_id])
    
    save_files(task_id, data["files_list"], files)
    
    run_data = get_run(task_id)
    webhook_data = output.get("webhook", None)
    if webhook_data:
        handle_webhooks(run_data, webhook_data, files)

    new_tasks_data = output.get("new_tasks", None)
    if new_tasks_data:
        handle_new_tasks(run_data, new_tasks_data)
    
def handle_webhooks(run_data, webhook_data, files):
    exit_code = run_data["exit_code"]
    
    webhook_name = webhook_data.get("channel_name", "MAIN")
    
    main_url = os.getenv(f"DISCORD_{webhook_name}_WEBHOOK_URL")
    log_url = os.getenv("DISCORD_LOG_WEBHOOK_URL")

    webhooks.send_webhook(log_url, webhooks.get_run_embed(run_data))
    
    custom_webhook = webhooks.get_custom_embed(run_data, webhook_data)
    webhooks.send_webhook(main_url, custom_webhook)
    
    log = get_file_by_name("log", files)
    log_str = log.file.read()
    # we need to read this file again later, when saving
    # so we need to seek back to pos 0, bc files can usually
    # only be read once
    log.file.seek(0)

    if exit_code != 0:
        webhooks.send_file(log_url, log_str)
    
def save_files(task_id, files_list, files):    
    for entry in files_list:
        hash = entry["name"]
        
        if entry["type"] == "run":
            path_prefix = os.path.join("runs", str(task_id))
        if entry["type"] == "global":
            path_prefix = "global"
        path = entry["path"]

        full_path = os.path.join(paths.FILES, path_prefix, path)
        parent_path = os.path.dirname(full_path)
        
        os.makedirs(parent_path, exist_ok=True)
        
        file = get_file_by_name(hash, files)
        
        with open(full_path, "wb") as f:
            f.write(file.file.read())

def handle_new_tasks(run_data, new_tasks_data):
    for new_task_data in new_tasks_data:
        script = new_task_data["script"]
        data = new_task_data.get("data", {})
        create_task(script, data)
            
def get_file_by_name(name, files):
    for file in files:
        if file.filename == name:
            return file
    return None

def get_run(task_id):
    rows = db.query("""
        SELECT * FROM tasks t
        LEFT JOIN runs r ON r.task_id = t.id
        WHERE r.task_id = ?;
        """, [task_id])
    if len(rows) == 0:
        return None
    return rows[0]