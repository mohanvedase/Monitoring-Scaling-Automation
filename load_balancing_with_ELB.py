import boto3
import json


elbv2 = boto3.client('elbv2')
ec2 = boto3.client('ec2')

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def describe_subnets(ec2, vpc_id):
    response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    return [subnet['SubnetId'] for subnet in response['Subnets']]

def create_target_group(elbv2, name, vpc_id):
    response = elbv2.create_target_group(
        Name=name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        HealthCheckProtocol='HTTP',
        HealthCheckPort='traffic-port',
        HealthCheckPath='/',
        HealthCheckIntervalSeconds=30,
        HealthCheckTimeoutSeconds=6,
        HealthyThresholdCount=3,
        UnhealthyThresholdCount=3,
    )
    return response['TargetGroups'][0]['TargetGroupArn']

def create_load_balancer(elbv2, name, subnets, security_groups):
    if isinstance(security_groups, str):
        security_groups = [security_groups]

    response = elbv2.create_load_balancer(
        Name=name,
        Subnets=subnets,
        SecurityGroups=security_groups,
        Scheme='internet-facing',
    )
    return response['LoadBalancers'][0]['LoadBalancerArn']

def register_targets(elbv2, target_group_arn, instance_ids):
    response = elbv2.register_targets(
        TargetGroupArn=target_group_arn,
        Targets=[{'Id': instance_id} for instance_id in instance_ids],
    )
    return response['ResponseMetadata']['HTTPStatusCode']

# Read data from JSON files
ec2_instances_data = read_json_file('ec2_instances.json')
configuration_data = read_json_file('configration.json')

# Extract VPC ID
vpc_id = ec2_instances_data[0].get('VpcId')

# Describe subnets
subnets = describe_subnets(boto3.client('ec2'), vpc_id)
print("Subnet IDs:", subnets)

# Create target groups
backend_target_group_arn = create_target_group(elbv2, configuration_data['BackendInstance']['ApplicationLB']['TargetGroup'], vpc_id)
frontend_target_group_arn = create_target_group(elbv2, configuration_data['FrontendInstance']['ApplicationLB']['TargetGroup'], vpc_id)

# Create load balancers
backend_lb_arn = create_load_balancer(elbv2,
                                      configuration_data['BackendInstance']['ApplicationLB']['ApplicationLBName'],
                                      subnets,
                                      configuration_data['BackendInstance']['ApplicationLB']['SecurityGroups'])

frontend_lb_arn = create_load_balancer(elbv2,
                                       configuration_data['FrontendInstance']['ApplicationLB']['ApplicationLBName'],
                                       subnets,
                                       configuration_data['FrontendInstance']['ApplicationLB']['SecurityGroups'])

# Register instances with target groups
backend_instance_ids = [instance['InstanceId'] for instance in ec2_instances_data if 'backend' in instance['Name']]
frontend_instance_ids = [instance['InstanceId'] for instance in ec2_instances_data if 'frontend' in instance['Name']]

backend_register_status = register_targets(elbv2, backend_target_group_arn, backend_instance_ids)
frontend_register_status = register_targets(elbv2, frontend_target_group_arn, frontend_instance_ids)

# Check registration status
if backend_register_status == 200:
    print('EC2 instances registered with the backend ALB successfully!')
else:
    print('Error registering EC2 instances with the backend ALB.')

if frontend_register_status == 200:
    print('EC2 instances registered with the frontend ALB successfully!')
else:
    print('Error registering EC2 instances with the frontend ALB.')
