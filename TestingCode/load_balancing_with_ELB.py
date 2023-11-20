import boto3
import json

# Now, you need to register your EC2 instances with the ALBs using the instances from the JSON file
with open('ec2_instances.json', 'r') as file:
    ec2_instances_data = json.load(file)

# Initialize the boto3 client for Elastic Load Balancing (ELB)
elbv2 = boto3.client('elbv2')

# Initialize the boto3 client for EC2
ec2 = boto3.client('ec2')

# Extract VPC ID from the first EC2 instance in the JSON file
if ec2_instances_data:
    vpc_id = ec2_instances_data[0].get('VpcId')
    if vpc_id:
        # Use the describe_subnets() function to get information about the subnets in the specified VPC
        response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])

        # Extract and print subnet IDs
        subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]
        print("Subnet IDs:", subnet_ids)
    else:
        print("VPC ID not found in the EC2 instances data.")
else:
    print("EC2 instances data is empty.")





# Define your target group attributes
backend_target_group_name = 'target-group-backend-using-boto3-G4'
frontend_target_group_name = 'target-group-frontend-using-boto3-G4'
protocol = 'HTTP'
port = 80
vpc_id = 'vpc-0c5a8881cff1146d8'  # Replace with your VPC ID

# Create the target group
backendresponse = elbv2.create_target_group(
    Name=backend_target_group_name,
    Protocol=protocol,
    Port=port,
    VpcId=vpc_id,
    HealthCheckProtocol='HTTP',
    HealthCheckPort='traffic-port',
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=6,
    HealthyThresholdCount=3,
    UnhealthyThresholdCount=3,
)

frontendresponse = elbv2.create_target_group(
    Name=frontend_target_group_name,
    Protocol=protocol,
    Port=port,
    VpcId=vpc_id,
    HealthCheckProtocol='HTTP',
    HealthCheckPort='traffic-port',
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=6,
    HealthyThresholdCount=3,
    UnhealthyThresholdCount=3,
)

# Extract the target group ARN from the response
backendtarget_group_arn = backendresponse['TargetGroups'][0]['TargetGroupArn']
frontendtarget_group_arn = frontendresponse['TargetGroups'][0]['TargetGroupArn']

# Print the ARN for reference
print(f'Created Target Group with ARN: {backendtarget_group_arn}')
print(f'Created Target Group with ARN: {frontendtarget_group_arn}')

# Use the describe_subnets() function to get information about the subnets in the specified VPC
response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])

# Extract and print subnet IDs
subnet_ids = [subnet['SubnetId'] for subnet in response['Subnets']]
print("Subnet IDs:", subnet_ids)


# Define your ALB attributes
backend_alb_name = 'application-lb-backend-using-boto3_G4'
frontend_alb_name = 'application-lb-frontend-using-boto3_G4'
subnets = subnet_ids #['subnet-0ea24e054cba9cad2', 'subnet-054d138c719f3f355','subnet-0ea185273ead71a27']  # Replace with your subnet IDs
security_groups = ['sg-0103a917e74448c29']  # Replace with your security group ID
load_balancer_scheme = 'internet-facing'  # You can change this to 'internal' if needed

# Create the Application Load Balancer
response = elbv2.create_load_balancer(
    Name=backend_alb_name,
    Subnets=subnets,
    SecurityGroups=security_groups,
    Scheme=load_balancer_scheme,
)

# Extract the ALB ARN from the response
alb_arn = response['LoadBalancers'][0]['LoadBalancerArn']

# Print the ARN for reference
print(f'Created ALB with ARN: {alb_arn}')

# Now, you need to register your EC2 instances with the ALB
# Initialize the boto3 client for EC2
ec2 = boto3.client('ec2')

# Replace these with the IDs of your EC2 instances
instance_ids = ['i-018a931e11f829ffa', 'i-07a9e4f76c4ff8cdd']

# Register the instances with the ALB target group
target_group_arn = 'arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-target-group/1234567890'  # Replace with your target group ARN
response = elbv2.register_targets(
    TargetGroupArn=target_group_arn,
    Targets=[{'Id': instance_id} for instance_id in instance_ids],
)

# Check the response for successful registration
if response['ResponseMetadata']['HTTPStatusCode'] == 200:
    print('EC2 instances registered with the ALB successfully!')
else:
    print('Error registering EC2 instances with the ALB.')

# Optionally, you can configure the ALB listener rules and routes as needed.
