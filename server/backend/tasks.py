import db_helper as db
import webhooks
import os

def get_tasks():
    rows = db.query("SELECT * FROM tasks t LEFT JOIN runs r ON r.task_id = t.id;")
    
    return rows

def create_task(script, path):
    db.exec("""
        INSERT INTO tasks (script, workspace_path)
        VALUES (?, ?);
        """, [script, path])

def get_next_task(allowed_scripts):
    interpolations = "?," * len(allowed_scripts)
    interpolations = interpolations[:-1]
    
    rows = db.query(f"""
        SELECT t.* FROM tasks t
        LEFT JOIN runs r ON r.task_id = t.id
        WHERE r.started_at IS NULL AND
        script IN ({interpolations});
        """, [*allowed_scripts])
        
    return rows

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
    
    main_url = os.getenv("DISCORD_MAIN_WEBHOOK_URL")
    log_url = os.getenv("DISCORD_LOG_WEBHOOK_URL")

    run_data = get_run(task_id)
    webhooks.send_webhook(log_url, webhooks.get_run_embed(run_data))
    
    webhook_data = output["webhook"]
    custom_webhook = webhooks.get_custom_embed(run_data, webhook_data)
    webhooks.send_webhook(main_url, custom_webhook)
    
    if exit_code != 0:
        log = get_file_by_name("log", files)
        log_str = log.file.read()

        webhooks.send_file(log_url, log_str)
        
    save_files(task_id, data["files_list"], files)

def save_files(task_id, files_list, files):
    os.makedirs("/app/workspace/files", exist_ok=True)
    
    for entry in files_list:
        hash = entry["name"]
        
        if entry["type"] == "run":
            path_prefix = os.path.join("runs", str(task_id))
        if entry["type"] == "global":
            path_prefix = "global"
        path = entry["path"]

        full_path = os.path.join("/app/workspace/files", path_prefix, path)
        parent_path = os.path.dirname(full_path)
        
        os.makedirs(parent_path, exist_ok=True)
        
        file = get_file_by_name(hash, files)
        
        with open(full_path, "wb") as f:
            f.write(file.file.read())

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