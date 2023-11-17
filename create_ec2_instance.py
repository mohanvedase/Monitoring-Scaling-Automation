import boto3
import time

ec2 = boto3.resource('ec2')

instance_params = {
    'ImageId': 'ami-0f5ee92e2d63afc18',
    'InstanceType': 't2.micro',
    'KeyName': 'boto3_G4',
    'SecurityGroupIds': ['sg-017c91bca422407e5'],
    'MinCount': 1,
    'MaxCount' : 1,
    'TagSpecifications': [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'backend_G4'
                },
                {
                    'Key': 'Purpose',
                    'Value': 'frontend_G4'
                }
            ]
        }
    ]
}


# Create a new EC2 instance
instances = ec2.create_instances(**instance_params)
instance = instances[0]
instance.wait_until_running()
# Add a loop to wait until the instance has a public IP address
while not instance.public_ip_address:
    time.sleep(15)  # Wait for 15 seconds before checking again
    instance.reload()  # Reload the instance information
    print("Waiting for public IP address...")
print(f"Instance ID: {instance.id}")
print(f"Instance Name: {instance.tags[0]['Value']}")
print(f"Public IP Address: {instance.public_ip_address}")

instances = ec2.create_instances(**instance_params)
instance = instances[0]
instance.wait_until_running()
# Add a loop to wait until the instance has a public IP address
while not instance.public_ip_address:
    time.sleep(5)  # Wait for 5 seconds before checking again
    instance.reload()  # Reload the instance information
    print("Waiting for public IP address...")
print(f"Instance ID: {instance.id}")
print(f"Instance Name: {instance.tags[0]['Value']}")
print(f"Public IP Address: {instance.public_ip_address}")
