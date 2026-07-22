import os

DOCKER_ROOT = "/app"
DOCKER_SCRIPT = os.path.join(DOCKER_ROOT, "script")
DOCKER_OUTPUT = os.path.join(DOCKER_ROOT, "output")
DOCKER_OUTPUT_RUN = os.path.join(DOCKER_OUTPUT, "run")
DOCKER_OUTPUT_GLOBAL = os.path.join(DOCKER_OUTPUT, "global")

RUNNER_ROOT = "/app/workspace/"
RUNNER_SCRIPTS = os.path.join("/app", "scripts")
RUNNER_OUTPUT = os.path.join(RUNNER_ROOT, "output")
RUNNER_OUTPUT_JSON = os.path.join(RUNNER_OUTPUT, "output.json")
RUNNER_OUTPUT_RUN = os.path.join(RUNNER_OUTPUT, "run")
RUNNER_OUTPUT_GLOBAL = os.path.join(RUNNER_OUTPUT, "global")

MACHINE_ROOT = "/var/lib/cexec-client/"
MACHINE_OUTPUT = os.path.join(MACHINE_ROOT, "output")