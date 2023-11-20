import boto3

sns = boto3.client('sns')

def lambda_handler(event, context):
    message = "Health issue detected. Please take action."
    sns.publish(
        TopicArn='arn:aws:sns:ap-south-1:295397358094:sns-boto3-G4',
        Message=message
    )
