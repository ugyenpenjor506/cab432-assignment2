from app import app
import jwt
import requests
from flask import request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.helper.SecretManager import get_secrets
import boto3
from app.helper.ParameterStore import get_cognito_domain

# Enable CORS for all routes
CORS(app)

# Replace these with your AWS Cognito settings
COGNITO_CLIENT_ID = get_secrets()['COGNITO_CLIENT_ID']
COGNITO_REGION =  get_secrets()['COGNITO_REGION']
COGNITO_POOL_ID = get_secrets()['COGNITO_POOL_ID']

 # Retrieve the Cognito domain from Parameter Store using the helper function
COGNITO_DOMAIN = get_cognito_domain()

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

class UserController:
    
    @app.route('/login_with_google')
    def login_with_google():
            try:
                # AWS Cognito Hosted UI URL for Google login
                redirect_url = f"https://{COGNITO_DOMAIN}/oauth2/authorize"
                response_type = "code"
                client_id = COGNITO_CLIENT_ID
                redirect_uri = "http://localhost:5005/callback"  # Your callback URI
                scope = "openid email"  # Minimal scope for Google login
                prompt = "login"  # Force Google login

                # Construct the login URL with the prompt=login parameter
                login_url = f"{redirect_url}?response_type={response_type}&client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&identity_provider=Google&prompt={prompt}"
                
                # Redirect the user to AWS Cognito's Hosted UI (Google login page)
                return redirect(login_url)

            except Exception as e:
                return f"Error: {str(e)}", 500
       


    @app.route('/callback')
    def callback():
        code = request.args.get('code')

        if not code:
            return jsonify({"error": "Authorization code not found"}), 400

        try:
            # Exchange the authorization code for tokens
            token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
            response = requests.post(token_url, data={
                'grant_type': 'authorization_code',
                'client_id': COGNITO_CLIENT_ID,
                'code': code,
                'redirect_uri': "http://localhost:5005/callback"
            }, headers={'Content-Type': 'application/x-www-form-urlencoded'})

            tokens = response.json()

            if 'id_token' in tokens:
                # Decode the ID token to get user info
                id_token = tokens['id_token']
                decoded_token = jwt.decode(id_token, options={"verify_signature": False})

                # Prepare response for API usage (avoid showing in browser directly)
                return jsonify({
                    "message": "Login with Google successful",
                    "email": decoded_token.get('email'),
                    "user_id": decoded_token.get('sub'),
                    "username": decoded_token.get('cognito:username'),
                    "token": id_token
                }), 200
            else:
                return jsonify({"error": "Failed to retrieve token"}), 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500


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
