import boto3
import gzip

sns = boto3.client('sns')

def lambda_handler(event, context):
    for record in event['Records']:
        # Get the S3 bucket and object key
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Download and unzip the ALB log file
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        log_content = gzip.decompress(response['Body'].read()).decode('utf-8')

        # Analyze the log for suspicious activities or high traffic
        if is_suspicious(log_content):
            # Send a notification via SNS
            sns.publish(
                TopicArn='Suspicious-Activity-Detected',
                Subject='Suspicious Activity Detected',
                Message='Potential DDoS attack or high traffic detected in ALB access logs.'
            )

def is_suspicious(log_content):
        # Convert log content to lowercase for case-insensitive checks
    log_content = log_content.lower()
    
    # Define keywords or patterns for suspicious activities
    suspicious_keywords = ['error', 'unauthorized', 'access denied', 'denial of service']
    
    # Check for the presence of suspicious keywords in the log content
    for keyword in suspicious_keywords:
        if keyword in log_content:
            return True  # Detected suspicious activity
    
    return False  # No suspicious activity detected

