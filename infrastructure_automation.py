import boto3

# Initialize the necessary boto3 clients
ec2 = boto3.client('ec2')
elbv2 = boto3.client('elbv2')
autoscaling = boto3.client('autoscaling')

def describe_default_vpc(ec2_client):
    response = ec2_client.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    return response['Vpcs'][0]['VpcId'] if response['Vpcs'] else None

def describe_subnets(ec2_client, vpc_id):
    response = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    return [subnet['SubnetId'] for subnet in response['Subnets']]

def deploy_infrastructure():
    # Create VPC
    ec2 = boto3.client('ec2')

    # Get the default VPC ID
    default_vpc_id = describe_default_vpc(ec2)

    if default_vpc_id:
        # Use the default VPC ID to work within the default VPC
        subnets_in_default_vpc = describe_subnets(ec2, default_vpc_id)

    # Create an Application Load Balancer (ALB)
    lb_response = elbv2.create_load_balancer(Name='', Subnets=[subnets_in_default_vpc])
    alb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']

    # Configure ALB listeners, target groups, and rules
    elbv2.create_listener(LoadBalancerArn=alb_arn, Protocol='HTTP', Port=80, DefaultActions=[{'Type': 'fixed-response', 'FixedResponseConfig': {'ContentType': 'text/plain', 'StatusCode': '200'}}])
    
    # Launch EC2 instances with a specific Amazon Machine Image (AMI)
    instance_response = ec2.run_instances(ImageId='ami-0f5ee92e2d63afc18', MinCount=2, MaxCount=2, InstanceType='t2.micro', KeyName='tg-backend-boto3-G4', SubnetId=subnets_in_default_vpc)
    instance_ids = [instance['InstanceId'] for instance in instance_response['Instances']]

    # Configure Auto Scaling for the instances
    asg_response = autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='my-asg',
        LaunchTemplate={'LaunchTemplateName': 'my-launch-template'},
        MinSize=2,
        MaxSize=5,
        DesiredCapacity=2,
        AvailabilityZones=['us-east-1a'],
        TargetGroupARNs=[],
        HealthCheckType='EC2',
        HealthCheckGracePeriod=300,
        InstanceType='t2.micro'
    )

    print("Infrastructure deployed successfully.")

def update_components():
     # Assuming you want to modify an ALB setting using boto3
    alb_name = 'applb-backend-boto3-G4'  # Replace with your ALB name
    new_alb_setting_value = 'new-value'  # Replace with the new setting value
    
    elbv2_client = boto3.client('elbv2')

    # Example: Modify a setting for the ALB (for instance, changing a security policy)
    try:
        response = elbv2_client.modify_load_balancer_attributes(
            LoadBalancerArn='applb-backend-boto3-G4',
            Attributes=[
                {
                    'Key': 'your-setting-key',
                    'Value': new_alb_setting_value
                },
            ]
        )
        print("ALB settings updated successfully.")
    except Exception as e:
        print("Error updating ALB settings:", e)

def tear_down_infrastructure():
    # Assuming you want to terminate EC2 instances and delete an ALB using boto3
    ec2_client = boto3.client('ec2')
    elbv2_client = boto3.client('elbv2')
    alb_name =''
    alb_arn = None

    # Retrieve the ARN of the ALB using its name
    albs = elbv2_client.describe_load_balancers(Names=[alb_name])
    if albs['LoadBalancers']:
        alb_arn = albs['LoadBalancers'][0]['LoadBalancerArn']
    else:
        print(f"No ALB found with the name: {alb_name}")
        return []

    # Retrieve target groups associated with the ALB
    target_groups = elbv2_client.describe_target_groups(LoadBalancerArn=alb_arn)
    instance_ids = []

    # Get instance IDs for each target group
    for target_group in target_groups['TargetGroups']:
        target_health = elbv2_client.describe_target_health(TargetGroupArn=target_group['TargetGroupArn'])
        for target in target_health['TargetHealthDescriptions']:
            instance_ids.append(target['Target']['Id'])


    # Terminate EC2 instances
    try:
        ec2_client.terminate_instances(InstanceIds=instance_ids)
        print("EC2 instances terminated.")
    except Exception as e:
        print("Error terminating instances:", e)

    # Delete ALB
    try:
        elbv2_client.delete_load_balancer(LoadBalancerArn=alb_arn)
        print("ALB deleted.")
    except Exception as e:
        print("Error deleting ALB:", e)

if __name__ == "__main__":
    action = input("Choose an action (deploy/update/teardown): ").lower()

    if action == "deploy":
        deploy_infrastructure()
    elif action == "update":
        update_components()
    elif action == "teardown":
        tear_down_infrastructure()
    else:
        print("Invalid action. Use 'deploy', 'update', or 'teardown'.")
