import json
import subprocess
from datetime import datetime, timedelta
from uuid import uuid4


def cfg_dsn(
        server_ip,
        server_port,
        public_key,
        short_id,
) -> (str, str):
    user_uuid = uuid4()

    vpn_dsn = f"vless://{user_uuid}@{server_ip}:{server_port}?"
    vpn_dsn += f"flow=xtls-rprx-vision-udp443&type=tcp&security=reality"
    vpn_dsn += "&fp=chrome&sni=www.microsoft.com"
    vpn_dsn += f"&pbk={public_key}&sid={short_id}&spx=/#{server_ip}"

    return vpn_dsn, user_uuid


# Function to add a new user to the Xray config
def add_xray_user(config_path, user_id, user_uuid, container_name, expiration_days=365):
    # Load the existing Xray config
    with open(config_path, 'r') as file:
        config = json.load(file)

    # Generate a new user UUID and expiration date
    expiration_date = (datetime.now() + timedelta(days=expiration_days)).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Create the new user object
    new_user = {
        "id": user_uuid,
        "alterId": 0,
        "user_id": user_id,
        "expiry": expiration_date,
        "flow": "xtls-rprx-vision"
    }

    # Find the inbound configuration for VLESS or VMess (adjust according to your setup)
    for inbound in config['inbounds']:
        if inbound['protocol'] in ['vmess', 'vless']:
            if 'settings' in inbound and 'clients' in inbound['settings']:
                inbound['settings']['clients'].append(new_user)
                print(f"Added new user: {user_id}, UUID: {user_uuid}")
                break
    else:
        print("No compatible inbound found for adding a new user.")
        return

    # Write the updated config back to the file
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)

    restart_container(container_name)


def restart_container(container_name):
    if not container_name:
        return

    try:
        subprocess.run(["docker", "restart", container_name], check=True)
        print(f"Container '{container_name}' restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart container '{container_name}': {e}")
