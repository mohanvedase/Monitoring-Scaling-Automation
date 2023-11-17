import boto3
import paramiko
import os

ec2 = boto3.resource('ec2')
instance_id = 'i-07466932945204313'  

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
    'nano TravelMemory/frontend/src/url.js && echo "export const baseUrl = "http://13.233.119.62"" >>TravelMemory/frontend/src/url.js',
    'cd TravelMemory/frontend/',
    'sudo npm install',
    'sudo apt-get install nginx -y',
    'sudo systemctl start nginx',
    'sudo unlink /etc/nginx/sites-enabled/default',
    'sudo cp /home/ubuntu/TravelMemory/mern-project /etc/nginx/sites-available/',
    'sudo ln -s /etc/nginx/sites-available/mern-project /etc/nginx/sites-enabled/',
    'sudo systemctl restart nginx',
    'sudo kill -9 $(sudo lsof -t -i:80)',
    'sudo npm start',

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
