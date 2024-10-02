import boto3
from app.helper.SecretManager import get_secrets

COGNITO_REGION =  get_secrets()['COGNITO_REGION']
# Initialize boto3 client for SSM (Parameter Store)
ssm = boto3.client('ssm', region_name=COGNITO_REGION)  # Update the region if necessary

# Parameter Store key for the Cognito domain
PARAMETER_NAME_DOMAIN = "/n11435542/cognito-domain"
PARAMETER_NAME_DBHOST = "/n11435542/db-host"

# Function to retrieve the Cognito domain from Parameter Store
def get_cognito_domain():
    try:
        response = ssm.get_parameter(Name=PARAMETER_NAME_DOMAIN)
        cognito_domain = response['Parameter']['Value']
        return cognito_domain
    except ssm.exceptions.ParameterNotFound:
        raise ValueError("Cognito domain not found in Parameter Store.")
    except Exception as e:
        raise RuntimeError(f"Error retrieving Cognito domain: {str(e)}")
    
# Function to retrieve the db host url from Parameter Store
def get_db_host():
    try:
        response = ssm.get_parameter(Name=PARAMETER_NAME_DBHOST)
        cognito_domain = response['Parameter']['Value']
        return cognito_domain
    except ssm.exceptions.ParameterNotFound:
        raise ValueError("Cognito domain not found in Parameter Store.")
    except Exception as e:
        raise RuntimeError(f"Error retrieving Cognito domain: {str(e)}")
