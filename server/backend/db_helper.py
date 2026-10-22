import paths

import os
import sqlite3
import uuid

conn = sqlite3.connect("/app/workspace/database.db")
cursor = conn.cursor()

def setup():
    exec("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            tag TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    exec("""
        CREATE TABLE IF NOT EXISTS runs (
            task_id INTEGER UNIQUE,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL,
            exit_code INTEGER DEFAULT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        );
    """)
    
    migrations = [do_migration_1_add_uuids]
    current_version = query("PRAGMA user_version;")[0]["user_version"]
    due_migrations = migrations[current_version:]
    
    if len(due_migrations) > 0:
        print(f"Migrating Database, currently {current_version}")
        for i, due_migration in enumerate(due_migrations):
            print(f"Executing Migration {i+current_version+1}")
            due_migration()
        new_version = len(migrations)
        print(f"Migrated Database, now {new_version}")
                
        exec(f"PRAGMA user_version = {new_version};")

    conn.commit()

def do_migration_1_add_uuids():    
    exec("""
        CREATE TABLE IF NOT EXISTS tasks_new (
            uuid TEXT PRIMARY KEY NOT NULL,
            script TEXT NOT NULL,
            priority INTEGER DEFAULT 0,
            tag TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    exec("""
        CREATE TABLE IF NOT EXISTS runs_new (
            uuid TEXT PRIMARY KEY NOT NULL,
            task_uuid TEXT NOT NULL,
            idx INTEGER NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL,
            exit_code INTEGER DEFAULT NULL,
            FOREIGN KEY(task_uuid) REFERENCES tasks(id)
        );
    """)
    
    tasks = query("SELECT * FROM tasks;")
    task_ids_map = {}
    for task in tasks:
        uuid = get_uuid()
        task_ids_map[task["id"]] = uuid
        
        exec("""
            INSERT INTO tasks_new (uuid, script, priority, tag, created_at)
            VALUES (?, ?, ?, ?, ?);
        """, (uuid, task["script"], task["priority"], task["tag"], task["created_at"]))

        old_path = os.path.join(paths.UPCOMING_RUNS_DEPRECATED, f"{task["id"]}.json")
        if os.path.exists(old_path):
            with open(old_path, "r") as f:
                data = f.read()
            new_path = os.path.join(paths.TASK_DEFS, f"{uuid}.json")
            with open(new_path, "w") as f:
                f.write(data)
            os.remove(old_path)
    os.rmdir(paths.UPCOMING_RUNS_DEPRECATED)

    runs = query("SELECT * FROM runs;")
    for index, run in enumerate(runs):
        uuid = get_uuid()
        task_uuid = task_ids_map[run["task_id"]]
        
        exec("""
            INSERT INTO runs_new (uuid, task_uuid, idx, started_at, completed_at, exit_code)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (uuid, task_uuid, index+1, run["started_at"], run["completed_at"], run["exit_code"]))
    
    exec("DROP TABLE tasks;")
    exec("DROP TABLE runs;")

    exec("ALTER TABLE tasks_new RENAME TO tasks;")
    exec("ALTER TABLE runs_new RENAME TO runs;")

def exec(query, data=[]):
    cursor.execute(query, data)
    conn.commit()

def query(query, data=[]):
    cursor.execute(query, data)
    raw_rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    rows = []
    for raw_row in raw_rows:
        row = dict(zip(columns, raw_row))
        rows.append(row)
        
    return rows

def last_row_id():
    return cursor.lastrowid

def get_uuid():
    return str(uuid.uuid4())