import os

DOCKER_ROOT = "/app"
DOCKER_WORKSPACE = os.path.join(DOCKER_ROOT, "workspace")
DOCKER_SCRIPT = os.path.join(DOCKER_ROOT, "script")
DOCKER_OUTPUT = os.path.join(DOCKER_ROOT, "output")
DOCKER_OUTPUT_RUN = os.path.join(DOCKER_OUTPUT, "run")
DOCKER_OUTPUT_GLOBAL = os.path.join(DOCKER_OUTPUT, "global")
DOCKER_INPUT = os.path.join(DOCKER_ROOT, "input")

RUNNER_ROOT = "/app/workspace/"
RUNNER_SCRIPTS = os.path.join("/app", "scripts")
RUNNER_OUTPUT = os.path.join(RUNNER_ROOT, "output")
RUNNER_OUTPUT_JSON = os.path.join(RUNNER_OUTPUT, "output.json")
RUNNER_OUTPUT_RUN = os.path.join(RUNNER_OUTPUT, "run")
RUNNER_OUTPUT_GLOBAL = os.path.join(RUNNER_OUTPUT, "global")
RUNNER_INPUT = os.path.join(RUNNER_ROOT, "input")

MACHINE_ROOT = "/var/lib/cexec-client/"
MACHINE_OUTPUT = os.path.join(MACHINE_ROOT, "output")
MACHINE_INPUT = os.path.join(MACHINE_ROOT, "input")