import boto3
import json

file_path = 'configration.json'

with open(file_path, 'r') as file:
    data = json.load(file)

# Initialize the EC2 client
ec2_client = boto3.client('ec2')

# Define the launch template parameters
launch_template_name = data['LaunchTemplate']['TemplateName']
instance_type = data['LaunchTemplate']['InstanceType']
image_id = data['LaunchTemplate']['ImageId']
key_name = data['LaunchTemplate']['Key']

# Describe default security groups
response = ec2_client.describe_security_groups(
    Filters=[
        {
            'Name': 'group-name',
            'Values': ['default']
        }
    ]
)

default_security_group_id = response['SecurityGroups'][0]['GroupId']
print(f"Default Security Group ID: {default_security_group_id}")

response = ec2_client.describe_launch_templates(
        LaunchTemplateNames=[launch_template_name]
    )
    
if response['LaunchTemplates']:
    launch_template_id = response['LaunchTemplates'][0]['LaunchTemplateId']
    print(f"Launch template '{launch_template_name}' already exists. Skipping creation.")
else:
    # Create the launch template
    response = ec2_client.create_launch_template(
        LaunchTemplateName=launch_template_name,
        VersionDescription='Initial version',
        LaunchTemplateData={
            'InstanceType': instance_type,
            'ImageId': image_id,
            'SecurityGroupIds': [default_security_group_id],
            'KeyName': key_name,
        }
    )
    launch_template_id = response['LaunchTemplate']['LaunchTemplateId']


# Retrieve the Launch Template ID from the response

print(f"Created Launch Template ID: {launch_template_id}")

# Update the Launch Template details in the JSON data
data['LaunchTemplate']['TemplateId'] = launch_template_id
data['LaunchTemplate']['SecurityGroupIds'] = default_security_group_id

# Write the updated data back to configration.json
with open(file_path, 'w') as file:
    json.dump(data, file, indent=2)


# Initialize the boto3 client for Auto Scaling
autoscaling = boto3.client('autoscaling')

# Replace these values with your own
asg_name = data['AutoScaling']['AutoScalingName']
launch_template_id = data['LaunchTemplate']['TemplateId']  # Replace with your launch template ID
launch_template_name = data['LaunchTemplate']['TemplateName']  # Replace with your launch template ID
min_size = data['AutoScaling']['MinSize']  # Minimum number of instances
max_size = data['AutoScaling']['MaxSize']  # Maximum number of instances
desired_capacity = data['AutoScaling']['DesiredCapacity']  # Initial desired capacity
instance_type = data['AutoScaling']['InstanceType']  # EC2 instance type
targetBackend = data['BackendInstance']['ApplicationLB']['TargetGroup']
targetFrontend = data['FrontendInstance']['ApplicationLB']['TargetGroup']
nameBackend = data['BackendInstance']['ApplicationLB']['ApplicationLBName']
nameFrontend = data['FrontendInstance']['ApplicationLB']['ApplicationLBName']

response = ec2_client.describe_launch_templates(
    LaunchTemplateIds=[launch_template_id]
)

if not response['LaunchTemplates']:
    print(f"Launch template with ID {launch_template_id} does not exist.")
else:
    print(f"Launch template with ID {launch_template_id} exists.")


# # Describe availability zones
response = ec2_client.describe_availability_zones()

availability_zones = [zone['ZoneName'] for zone in response['AvailabilityZones']]
print(f"Available Availability Zones: {availability_zones}")

# Create an Auto Scaling Group
response = autoscaling.create_auto_scaling_group(
    AutoScalingGroupName=asg_name,
    LaunchTemplate={
        'LaunchTemplateName': launch_template_name,
    },
    MinSize=min_size,
    MaxSize=max_size,
    DesiredCapacity=desired_capacity,
    AvailabilityZones=availability_zones,  # Replace with your desired availability zones
    #TargetGroupARNs=[target_group_arn_backend,target_group_arn_frontend],  # Specify target groups if you're using an Application Load Balancer
    HealthCheckType='EC2',
    HealthCheckGracePeriod=300,  # Adjust this value as needed
)

print(f'Created Auto Scaling Group: {asg_name}')

# Set up scaling policies based on CPU utilization
response_cpu = autoscaling.put_scaling_policy(
    AutoScalingGroupName=asg_name,
    PolicyName='CPUUtilizationScalingPolicy',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageCPUUtilization',
        },
        'TargetValue': 60,  # Adjust this value based on your requirements
        'DisableScaleIn': False
    }
)

# Set up scaling policies based on network traffic (NetworkIn)
response_network = autoscaling.put_scaling_policy(
    AutoScalingGroupName=asg_name,
    PolicyName='NetworkTrafficScalingPolicy',
    PolicyType='TargetTrackingScaling',
    TargetTrackingConfiguration={
        'PredefinedMetricSpecification': {
            'PredefinedMetricType': 'ASGAverageNetworkIn',  # Adjust if required
        },
        'TargetValue': 10000000,  # Adjust this value based on your requirements
        'DisableScaleIn': False
    }
)

# # Configure scaling policies based on CPU utilization
# cpu_scaling_policy_name = 'CPUUtilizationScalingPolicy'
# cpu_target_value = 60  # Example: Scale out if CPU > 60%
# cpu_scale_out_adjustment = 1
# cpu_scale_in_adjustment = -1

# response = autoscaling.put_scaling_policy(
#     AutoScalingGroupName=asg_name,
#     PolicyName=cpu_scaling_policy_name,
#     PolicyType='TargetTrackingScaling',
#     TargetTrackingConfiguration={
#         'PredefinedMetricSpecification': {
#             'PredefinedMetricType': 'ASGAverageCPUUtilization',
#         },
#         'TargetValue': cpu_target_value,
#     }
# )

# # Attach the scaling policy to the Auto Scaling Group
# policy_arn = response['PolicyARN']

# # Assuming you have the necessary parameters
# adjustment_type = 'ChangeInCapacity'
# scaling_adjustment = 1  # Change this according to your requirement
# cooldown = 300  # Adjust the cooldown period as needed

# response = autoscaling.put_scaling_policy(
#         AutoScalingGroupName=asg_name,
#         PolicyName='ScalingPolicy',
#         AdjustmentType=adjustment_type,
#         ScalingAdjustment=scaling_adjustment,
#         Cooldown=cooldown
#     )

# print(f'Configured CPU scaling policy: {cpu_scaling_policy_name}')
