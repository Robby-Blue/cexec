import os
import json
import docker
docker_client = docker.from_env()

def run_script_container(script_name):
    config = get_config(script_name)
    image_name = config["image"]
    
    machine_scripts_path = os.getenv("SCRIPTS_PATH")
    machine_script_path = os.path.join(machine_scripts_path, script_name)
    
    script_mount = docker.types.Mount(target="/app/script",
        source=machine_script_path, type="bind")
    output_mount = docker.types.Mount(target="/app/output",
        source="/var/lib/cexec-client/output", type="bind")
    
    container = docker_client.containers.run(image_name,
        detach=True, tty=True, mounts=[script_mount, output_mount]
    )
    
    res = container.exec_run(["sh", "entrypoint.sh"],
        workdir="/app/script")

    code = res.exit_code
    output = res.output.decode("UTF-8")
    
    return code, output

def get_config(script_name):
    script_path = os.path.join("/app/scripts", script_name, "config.json")
    with open(script_path, "r") as f:
        return json.load(f)