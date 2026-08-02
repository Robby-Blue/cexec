import os
import json
import docker
import paths

docker_client = docker.from_env()

def run_script_container(script_name):
    config = get_config(script_name)
    image_name = config["image"]
    
    machine_scripts_path = os.getenv("SCRIPTS_PATH")
    machine_script_path = os.path.join(machine_scripts_path, script_name)
    
    workspace_mount = docker.types.Mount(target=paths.DOCKER_WORKSPACE,
        source=None, type="tmpfs")
    script_mount = docker.types.Mount(target=paths.DOCKER_SCRIPT,
        source=machine_script_path, type="bind", read_only=True)
    output_mount = docker.types.Mount(target=paths.DOCKER_OUTPUT,
        source=paths.MACHINE_OUTPUT, type="bind")
    input_mount = docker.types.Mount(target=paths.DOCKER_INPUT,
        source=paths.MACHINE_INPUT, type="bind", read_only=True)

    container = docker_client.containers.run(image_name,
        detach=True, tty=True,
        mounts=[workspace_mount, script_mount, output_mount, input_mount]
    )
    
    entry_path = os.path.join(paths.DOCKER_SCRIPT, "entrypoint.sh")
    
    res = container.exec_run(["sh", entry_path],
        workdir=paths.DOCKER_WORKSPACE)

    code = res.exit_code
    output = res.output.decode("UTF-8")
    
    return code, output

def get_config(script_name):
    script_path = os.path.join(paths.RUNNER_SCRIPTS, script_name, "config.json")
    with open(script_path, "r") as f:
        return json.load(f)