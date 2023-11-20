import boto3
import json

# Load configration information from a JSON file
with open('configration.json', 'r') as json_file:
    configration_info = json.load(json_file)


ec2 = boto3.resource('ec2')

user_data = """#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y ec2-instance-connect
"""

instance_params = {
    'ImageId': 'ami-0f5ee92e2d63afc18',
    'InstanceType': 't2.micro',
    'KeyName': 'boto3_G4',
    'MinCount': 1,
    'MaxCount': 1,
    'UserData': user_data,
    'TagSpecifications': [
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': ''
                }
            ]
        },
    ],
}

instances_info = []

# Create the instances
for instance_name in ['backendusingboto3_1_G4', 'backendusingboto3_2_G4', 'frontendusingboto3_1_G4', 'frontendusingboto3_2_G4']:
    instance_params['TagSpecifications'][0]['Tags'][0]['Value'] = instance_name
    instances = ec2.create_instances(**instance_params)
    
    # Collect information about the created instances
    for instance in instances:
        instance_info = {
            'InstanceId': instance.id,
            'InstanceType': instance.instance_type,
            'ImageId': instance.image_id,
            'VpcId': instance.vpc_id,
            'KeyName': instance.key_name,
            'Name': instance_name,
        }
        instances_info.append(instance_info)

# Save instance information to a JSON file
with open('ec2_instances.json', 'w') as json_file:
    json.dump(instances_info, json_file, indent=2)

print("Instances created and information saved to 'ec2_instances.json' file.")