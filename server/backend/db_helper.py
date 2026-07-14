import sqlite3

conn = sqlite3.connect("/app/workspace/database.db")
cursor = conn.cursor()

def setup():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            script TEXT NOT NULL,
            workspace_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER UNIQUE,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP DEFAULT NULL,
            exit_code INTEGER DEFAULT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        );
    """)

    conn.commit()

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