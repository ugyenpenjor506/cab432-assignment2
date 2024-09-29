from app import app
import jwt
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.helper.SecretManager import get_secrets

import boto3

# Enable CORS for all routes
CORS(app)

# Replace these with your AWS Cognito settings
COGNITO_CLIENT_ID = get_secrets()['COGNITO_CLIENT_ID']
COGNITO_REGION =  get_secrets()['COGNITO_REGION']
COGNITO_POOL_ID = get_secrets()['COGNITO_POOL_ID']

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

class UserController:
    
    @app.route('/create_user', methods=['POST'])
    def create_user():
        data = request.get_json()
        username = data.get('username')  # This should be a unique username (not an email)
        email = data.get('email')        # The user's email
        password = data.get('password')

        if not username or not password or not email:
            return jsonify({
                "error": "Username, email, and password are required",
                "status": "fail",
                "code": 400
            }), 400

        try:
            # Sign up user in AWS Cognito
            response = cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,  # Use username, not email
                Password=password,
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    }
                ]
            )

            # Manually confirm the user sign-up (for testing or internal use)
            cognito_client.admin_confirm_sign_up(
                UserPoolId=COGNITO_POOL_ID,
                Username=username  # Confirm using the same username
            )

            return jsonify({
                "message": "User signed up and confirmed successfully",
                "status": "success",
                "code": 200
            }), 200

        except cognito_client.exceptions.UsernameExistsException:
            return jsonify({
                "error": "Username already exists",
                "status": "fail",
                "code": 409
            }), 409
        except Exception as e:
            return jsonify({
                "error": str(e),
                "status": "fail",
                "code": 500
            }), 500
            
            
@app.route('/login', methods=['POST'])
def login():
    SECRET_KEY = 'hg54376*6'
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({
            "error": "Username/email and password are required",
            "status": "fail",
            "code": 400
        }), 400

    try:
        # Initiating Auth using USER_PASSWORD_AUTH flow
        response = cognito_client.initiate_auth(
            ClientId=COGNITO_CLIENT_ID,
            AuthFlow='USER_PASSWORD_AUTH',  # Using USER_PASSWORD_AUTH flow
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']

        # Decode the JWT token to extract user information
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})

        user_id = decoded_token.get('sub')  # Extract the user ID (sub) from the token
        extracted_username = decoded_token.get('cognito:username')  # Extract the username

        return jsonify({
            "message": "Login successful",
            "status": "success",
            "code": 200,
            "token": id_token,
            "user_id": user_id,  # Include the user ID in the response
            "username": extracted_username  # Include the username from the decoded token
        }), 200

    except cognito_client.exceptions.NotAuthorizedException:
        return jsonify({
            "error": "Invalid username/email or password",
            "status": "fail",
            "code": 401
        }), 401
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "fail",
            "code": 500
        }), 500

        