import boto3


# Initialize AWS clients
ec2 = boto3.client('ec2')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')
client = boto3.client('elbv2')

# Specify your ALB name and desired health check threshold
alb_name = 'applb-backend-boto3-G4'
health_check_threshold = 3  # Number of consecutive failures before taking action

def lambda_handler(event, context):

    alb_arn = None

    # Retrieve the ARN of the ALB using its name
    albs = client.describe_load_balancers(Names=[alb_name])
    if albs['LoadBalancers']:
        alb_arn = albs['LoadBalancers'][0]['LoadBalancerArn']
    else:
        print(f"No ALB found with the name: {alb_name}")
        return []

    # Retrieve target groups associated with the ALB
    target_groups = client.describe_target_groups(LoadBalancerArn=alb_arn)
    instance_ids = []

    # Get instance IDs for each target group
    for target_group in target_groups['TargetGroups']:
        target_health = client.describe_target_health(TargetGroupArn=target_group['TargetGroupArn'])
        for target in target_health['TargetHealthDescriptions']:
            instance_ids.append(target['Target']['Id'])

    # Loop through instances
    for instance_id in instance_ids:
        # Check the health of the instance via custom logic or use CloudWatch Alarms
        if is_instance_unhealthy(instance_id):
            # Get instance details
            instance = ec2.describe_instances(InstanceIds=[instance_id])['Reservations'][0]['Instances'][0]

            # Capture a snapshot for debugging purposes
            snapshot_description = f"Snapshot for unhealthy instance: {instance_id}"
            snapshot_id = ec2.create_snapshot(Description=snapshot_description, VolumeId=instance['BlockDeviceMappings'][0]['Ebs']['VolumeId'])['SnapshotId']

            # Terminate the problematic instance
            ec2.terminate_instances(InstanceIds=[instance_id])

            # Notify administrators
            message = f"Instance {instance_id} failed health checks and was terminated. Snapshot ID: {snapshot_id}"
            sns.publish(TopicArn='sns-boto3-G4', Message=message, Subject='Web Application Health Check Alert')

def is_instance_unhealthy(instance_id):
    alarm_name = f'InstanceHealthCheck-{instance_id}'

    #create_instance_health_check_alarm(instance_id)
    # Check if the CloudWatch Alarm exists for the given instance
    response = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
    
    #return True
    # If the alarm exists and is in ALARM state, consider the instance unhealthy
    if response['MetricAlarms'] and response['MetricAlarms'][0]['StateValue'] == 'ALARM':
        return True
    else:
        return False

def create_instance_health_check_alarm(instance_id):
    cloudwatch = boto3.client('cloudwatch')

    alarm_name = f'InstanceHealthCheck-{instance_id}'

    # Define your alarm parameters
    alarm_params = {
        'AlarmName': alarm_name,
        'AlarmDescription': f'Health check for instance {instance_id}',
        'Namespace': 'AWS/EC2',
        'MetricName': 'StatusCheckFailed',
        'Dimensions': [
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        'ComparisonOperator': 'GreaterThanThreshold',
        'EvaluationPeriods': 1,
        'Period': 60,
        'Threshold': 0,
        'Statistic': 'Maximum',
        'ActionsEnabled': False, 
        'AlarmActions': [], 
        'OKActions': [],
        'InsufficientDataActions': [],
    }

    # Create the alarm if it doesn't exist
    try:
        cloudwatch.put_metric_alarm(**alarm_params)
        print(f"Alarm {alarm_name} created for instance {instance_id}")
    except cloudwatch.exceptions.AlreadyExistsException:
        print(f"Alarm {alarm_name} already exists for instance {instance_id}")

lambda_handler(None,None)