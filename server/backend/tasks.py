import db_helper as db

def get_tasks():
    rows = db.query("SELECT * FROM tasks;")
    
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
        SELECT * FROM tasks WHERE 
        started_at IS NULL AND
        script IN ({interpolations});
        """, [*allowed_scripts])
        
    return rows

def mark_started(id):
    db.exec("""
        UPDATE tasks SET started_at = CURRENT_TIMESTAMP
        WHERE id=?;
        """, [id])
    
def mark_completed(id):
    db.exec("""
        UPDATE tasks SET completed_at = CURRENT_TIMESTAMP
        WHERE id=?;
        """, [id])