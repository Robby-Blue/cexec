import os

ROOT = "/app/workspace/"
FILES = os.path.join(ROOT, "files")
FILES_RUNS = os.path.join(FILES, "runs")
FILES_GLOBAL = os.path.join(FILES, "global")
UPCOMING_RUNS_DEPRECATED = os.path.join(ROOT, "upcoming_runs")
TASK_DEFS = os.path.join(ROOT, "task_defs")

os.makedirs(FILES, exist_ok=True)
os.makedirs(FILES_RUNS, exist_ok=True)
os.makedirs(FILES_GLOBAL, exist_ok=True)
os.makedirs(TASK_DEFS, exist_ok=True)