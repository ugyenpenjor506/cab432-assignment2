import boto3
import json
import os

# Initialize Secrets Manager client
secrets_client = boto3.client('secretsmanager', region_name='ap-southeast-2')

# Secret name (use the secret name or ARN stored in AWS Secrets Manager)
secret_name = "n1234567-assignment2"

def get_secrets():
        """
        Function to retrieve secrets from AWS Secrets Manager
        """
        try:
            # Get secret value from AWS Secrets Manager
            response = secrets_client.get_secret_value(SecretId=secret_name)

            # Check if the secret is stored as a string (JSON formatted)
            if 'SecretString' in response:
                secret = response['SecretString']
                # Parse JSON and return the secret values
                return json.loads(secret)
            else:
                raise ValueError("Secret is not in string format.")
        except Exception as e:
            raise Exception(f"Error retrieving secret: {str(e)}")
        