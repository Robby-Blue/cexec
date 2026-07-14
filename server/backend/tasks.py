import db_helper as db
import webhooks

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

def complete_run(task_id, exit_code, output):
    db.exec("""
        UPDATE runs SET
        completed_at = CURRENT_TIMESTAMP,
        exit_code = ?
        WHERE task_id = ?;
        """, [exit_code, task_id])
    
    
    run_data = get_run(task_id)
    webhooks.send_webhook(webhooks.get_run_embed(run_data))
    
    webhook_data = output["webhook"]
    custom_webhook = webhooks.get_custom_embed(run_data, webhook_data)
    webhooks.send_webhook(custom_webhook)
    
def get_run(task_id):
    rows = db.query("""
        SELECT * FROM tasks t
        LEFT JOIN runs r ON r.task_id = t.id
        WHERE r.task_id = ?;
        """, [task_id])
    if len(rows) == 0:
        return None
    return rows[0]