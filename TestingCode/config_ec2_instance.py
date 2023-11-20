import boto3
import paramiko
import os

ec2 = boto3.resource('ec2')
instance_id = 'i-0e42e0da8733f0c06'  

instance = ec2.Instance(instance_id)
public_ip = instance.public_ip_address
key_name = 'boto3_G4'  

ssh_client = paramiko.SSHClient()

# Automatically add the server's host key (this is insecure and for demonstration purposes only)
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

current_directory = os.getcwd()
private_key_file_name = 'boto3_G4.pem'

script_path =   os.path.join(current_directory,'backend_script.sh')

# Connect to the EC2 instance
private_key_path = os.path.join(current_directory, private_key_file_name)
ssh_client.connect(public_ip, username='ubuntu', key_filename=private_key_path)

# Run commands on the EC2 instance
commands = [
    f'sudo bash {script_path}'
   # 'sudo apt-get update',
    #'sudo apt-get remove nodejs',
    #'curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -',
    # 'sudo apt-get update',
    # 'sudo apt-get install -y nodejs',
#     'sudo apt-get install -y npm',
#     'sudo apt-get install -y nginx',
#     'git clone https://github.com/abhijitganeshshinde/TravelMemory.git',
#    'cd TravelMemory/backend/ && touch .env && echo "MONGO_URI=\'mongodb+srv://abhi:bi39msm5Vo8G6gyZ@cluster0.bta0sbt.mongodb.net/travelmemory\'" > .env',
#    'echo "PORT=3000" >> TravelMemory/backend/.env'

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
