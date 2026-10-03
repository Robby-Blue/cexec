import os
import json
import docker
import paths
from datetime import datetime

docker_client = docker.from_env()

def run_script_container(script_name):
    config = get_config(script_name)
    image_name = config["image"]
    
    machine_scripts_path = os.getenv("SCRIPTS_PATH")
    machine_script_path = os.path.join(machine_scripts_path, script_name)
    
    workspace_mount = docker.types.Mount(target=paths.DOCKER_WORKSPACE,
        source=None)
    script_mount = docker.types.Mount(target=paths.DOCKER_SCRIPT,
        source=machine_script_path, type="bind", read_only=True)
    output_mount = docker.types.Mount(target=paths.DOCKER_OUTPUT,
        source=paths.MACHINE_OUTPUT, type="bind")
    input_mount = docker.types.Mount(target=paths.DOCKER_INPUT,
        source=paths.MACHINE_INPUT, type="bind", read_only=True)
    vars_mount = docker.types.Mount(target=paths.DOCKER_VARS,
        source=paths.MACHINE_VARS, type="bind", read_only=True)

    container = docker_client.containers.run(image_name,
        detach=True, tty=True,
        mounts=[workspace_mount, script_mount, output_mount, input_mount, vars_mount]
    )
    
    entry_path = os.path.join(paths.DOCKER_SCRIPT, "entrypoint.sh")
    
    api = container.client.api
    exec_id = api.exec_create(
        container.id,
        ["sh", entry_path],
        workdir=paths.DOCKER_WORKSPACE,
    )["Id"]

    lines = []
    for line in iter_lines(api.exec_start(exec_id, stream=True)):
        time = datetime.now().strftime("%H:%M:%S")
        timed_line = f"[{time}] {line}"
        print(f"{timed_line}")
        lines.append(timed_line)

    code = api.exec_inspect(exec_id)["ExitCode"]
    output = "\n".join(lines)
    return code, output

def iter_lines(stream):
    buf = b""
    for chunk in stream:
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            yield line.decode(errors="replace")
    if buf:
        yield buf.decode(errors="replace")

def get_config(script_name):
    script_path = os.path.join(paths.RUNNER_SCRIPTS, script_name, "config.json")
    with open(script_path, "r") as f:
        return json.load(f)