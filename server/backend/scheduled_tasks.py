from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

import db_helper as db
import tasks

with open("config.json") as f:
    scheduled_tasks = json.load(f)["scheduled_tasks"]

def create_scheduled_tasks():
    for scheduled_task in scheduled_tasks:
        create_scheduled_task(scheduled_task)

def create_scheduled_task(scheduled_task):
    if not should_create_scheduled_task(scheduled_task):
        return
    tasks.create_task(
        scheduled_task["script"],
        scheduled_task.get("data", {}),
        scheduled_task["tag"]
    )
    
def should_create_scheduled_task(scheduled_task):
    tag = scheduled_task["tag"]
    
    rows = db.query("""
        SELECT * FROM tasks t
        LEFT JOIN runs r ON r.task_id = t.id
        WHERE t.tag = ?;
        """, [tag])
    
    if len(rows) == 0:
        return True
    last_completed = None
    
    for row in rows:
        utc_completed = row["completed_at"]
        if not utc_completed:
            return False
        dt = datetime.strptime(utc_completed, '%Y-%m-%d %H:%M:%S')
    
        if last_completed is None or dt > last_completed:
            last_completed = dt
    
    return scheduled_time_passed(last_completed, datetime.now(), scheduled_task["schedule"])

def scheduled_time_passed(last_completed, now, schedule):
    schedule_type = schedule["type"]

    if schedule_type == "daily":
        candidate = last_completed.replace(
            hour=schedule["hour"],
            minute=0, second=0, microsecond=0)
        if candidate < last_completed:
            candidate += relativedelta(days=1)

        return candidate < now
    if schedule_type == "weekly":
        candidate = last_completed.replace(
            hour=schedule["hour"],
            minute=0, second=0, microsecond=0)
        candidate += relativedelta(weekday=schedule["weekday"])
        if candidate < last_completed:
            candidate += relativedelta(weeks=1)

        return candidate < now
    if schedule_type == "monthly":
        candidate = last_completed.replace(
            day=schedule["day"],
            hour=schedule["hour"],
            minute=0, second=0, microsecond=0)
        if candidate < last_completed:
            candidate += relativedelta(months=1)

        return candidate < now