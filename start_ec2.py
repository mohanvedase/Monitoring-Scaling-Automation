import boto3
import json

# Load JSON data from a file
with open('ec2_instances.json') as json_file:
    instances_data = json.load(json_file)

# Initialize a Boto3 EC2 client
ec2 = boto3.client('ec2')

# Start each EC2 instance
for instance_info in instances_data:
    instance_id = instance_info['InstanceId']
    
    # Start the instance
    ec2.start_instances(InstanceIds=[instance_id])
    
    print(f"Started EC2 instance with ID: {instance_id}")
