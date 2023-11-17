import boto3
import paramiko
import os

ec2 = boto3.resource('ec2')
instance_id = 'i-07b8c1d294229d88c'  

instance = ec2.Instance(instance_id)
public_ip = instance.public_ip_address
key_name = 'boto3_G4'  

ssh_client = paramiko.SSHClient()

# Automatically add the server's host key (this is insecure and for demonstration purposes only)
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

current_directory = os.getcwd()
private_key_file_name = 'boto3_G4.pem'

# Connect to the EC2 instance
#private_key_path = os.path.join(current_directory, private_key_file_name)
private_key_path = 'C:/Users/Admin/boto3_G4.pem'
ssh_client.connect(public_ip, username='ubuntu', key_filename=private_key_path)

# Run commands on the EC2 instance
commands = [
    'sudo apt-get update',
    'sudo apt-get remove nodejs',
    'curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -',
    'sudo apt-get update',
    'sudo apt-get install -y nodejs',
    'git clone https://github.com/UnpredictablePrashant/TravelMemory.git',
    'cd /home/ubuntu/TravelMemory/backend/ && touch .env && echo "mongodb+srv://mohankrishna19:TmrDh1yeaM1dhGE0@cluster1.zdinkmb.mongodb.net/travelmemory" >> .env',
    'echo "PORT=80" >> TravelMemory/backend/.env',
    'cd /home/ubuntu/TravelMemory/backend',
    'sudo apt-get install npm -y',
    'sudo apt-get install nginx -y',
    'sudo unlink /etc/nginx/sites-enabled/default',
    'sudo cp /home/ubuntu/TravelMemory/backend/mern-project /etc/nginx/sites-available/',
    'sudo ln -s /etc/nginx/sites-available/mern-project /etc/nginx/sites-enabled/',
    'sudo systemctl restart nginx',
    'sudo kill -9 $(sudo lsof -t -i:80)',
    'sudo node index.js -p 80',

]

try:

     for command in commands:
        print(f"Executing command: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print(f"Command Output:\n{output}")

        if error:
            print(f"Command Error:\n{error}")

finally:
    # Close the SSH connection
    ssh_client.close()
