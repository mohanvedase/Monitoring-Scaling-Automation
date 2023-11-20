import boto3
import os
from fabric import Connection
import json

ec2 = boto3.resource('ec2')

# Load instance information from a JSON file
with open('ec2_instances.json', 'r') as json_file:
    instance_info = json.load(json_file)

current_directory = os.getcwd()
private_key_file_name = 'boto3_G4.pem'
private_key_path = os.path.join(current_directory, private_key_file_name)


def is_package_installed(c, package_name):
    result = c.run(f'dpkg -l | grep {package_name}', warn=True)
    return result.exited == 0

# Define a function to run remote commands on an instance
def run_remote_commands(script_commands, public_ip):
    host = public_ip
    user = 'ubuntu'
    key_filename = private_key_path  # Modify this to your private key file path

    # Establish an SSH connection
    with Connection(
        host=host,
        user=user,
        connect_kwargs={"key_filename": key_filename}
    ) as c:
        for command in script_commands:
            try:
                result = c.run(command, hide=True)
                print(f"Command Output for '{command}':")
                print(result.stdout)
            except Exception as e:
                print(f"Command '{command}' failed with an exception: {str(e)}")
                continue  # Continue to the next command

if __name__ == "__main__":
    # Define nginx_config
    nginx_config = """
    server {
      listen 80;
      listen [::]:80;
      server_name _;

      location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
      }
    }
    """
    backend_commands_systemd_unit = """
[Unit]
Description=TravelMemory Application
After=network.target

[Service]
ExecStart=/usr/bin/node /home/ubuntu/TravelMemory/backend/index.js
WorkingDirectory=/home/ubuntu/TravelMemory/backend/
Restart=always
User=ubuntu
Group=ubuntu
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
"""

    frontend_commands_systemd_unit = """
[Unit]
Description=TravelMemory Application
After=network.target

[Service]
ExecStart=/usr/bin/serve -s build -p 3000
WorkingDirectory=/home/ubuntu/TravelMemory/frontend/
Restart=always
User=ubuntu
Group=ubuntu
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
"""


    # Define the script_commands for backend and frontend instances
    backend_commands = [
        'sudo apt-get update -y',
        'curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -',
        'sudo apt-get install -y nodejs',
        'sudo apt-get install -y nginx',
        'sudo unlink /etc/nginx/sites-enabled/default',
        'git clone https://github.com/abhijitganeshshinde/TravelMemory.git',
        'cd TravelMemory/backend/ && touch .env && echo "MONGO_URI=\'mongodb+srv://abhi:bi39msm5Vo8G6gyZ@cluster0.bta0sbt.mongodb.net/travelmemory\'" > .env',
        'echo "PORT=3000" >> TravelMemory/backend/.env',
        'cd TravelMemory/backend/ && npm install',
        f'echo \'{nginx_config}\' | sudo tee /etc/nginx/sites-available/travelmemory',
        'sudo ln -s /etc/nginx/sites-available/travelmemory /etc/nginx/sites-enabled/',
        'sudo nginx -t',
        'sudo systemctl reload nginx',
        f'echo \'{backend_commands_systemd_unit}\' | sudo tee /etc/systemd/system/travelmemory.service',
        'cd /etc/systemd/system/ && sudo systemctl enable travelmemory.service',
        'cd /etc/systemd/system/ && sudo systemctl start travelmemory.service',
        'sudo systemctl restart nginx'
    ]

    frontend_commands = [
        'sudo apt-get update -y',
        'curl -sL https://deb.nodesource.com/setup_18.x | sudo -E bash -',
        'sudo apt-get install -y nodejs',
        'sudo apt-get install -y nginx',
        'sudo unlink /etc/nginx/sites-enabled/default',
        'sudo npm install -g serve',
        'git clone https://github.com/abhijitganeshshinde/TravelMemory.git',
        f'echo "export const baseUrl = \\"http://$backendpublic_ip\\"" > TravelMemory/frontend/src/url.js',  # Use public_ip here
        'cd TravelMemory/frontend/ && npm install',
        'cd TravelMemory/frontend/ && npm run build',
        f'echo \'{nginx_config}\' | sudo tee /etc/nginx/sites-available/travelmemory',
        'sudo ln -s /etc/nginx/sites-available/travelmemory /etc/nginx/sites-enabled/',
        'sudo nginx -t',
        'sudo systemctl reload nginx',
        f'echo \'{frontend_commands_systemd_unit}\' | sudo tee /etc/systemd/system/travelmemory.service',
        'cd /etc/systemd/system/ && sudo systemctl enable travelmemory.service',
        'cd /etc/systemd/system/ && sudo systemctl start travelmemory.service',
        'sudo systemctl restart nginx'
    ]

    backend_public_ips = []
    # Configure the instances
    for instance in instance_info:
        instance_id = instance['InstanceId']  # Extract public IP from instance information
        ec2 = boto3.resource('ec2')
        instance_details = ec2.Instance(instance_id)
        public_ip = instance_details.public_ip_address
                
        # Run remote commands for the current instance (either backend or frontend)               
        if 'backend' in instance['Name']:
          backend_public_ips.append(public_ip)
          commands = backend_commands
        elif 'frontend' in instance['Name']:
          commands = frontend_commands

        if 'frontendusingboto3_1' in instance['Name']:
            commands = [command.replace('$backendpublic_ip', backend_public_ips[0]) for command in commands]
        elif 'frontendusingboto3_2' in instance['Name']:
            commands = [command.replace('$backendpublic_ip', backend_public_ips[1]) for command in commands]

        commands = [command.replace('$public_ip', public_ip) for command in commands]
        
        print(commands)
        run_remote_commands(commands, public_ip)