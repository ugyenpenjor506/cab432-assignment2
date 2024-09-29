from functools import wraps
from flask import request, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from app.helper.SecretManager import get_secrets


GOOGLE_CLIENT_ID = get_secrets()['GOOGLE_CLIENT_ID']

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if the token is provided in the request headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]  # Extract the token after 'Bearer'
        
        if not token:
            return jsonify({"message": "Token is missing", "status": "fail", "code": 401}), 401

        try:
            # Step 1: Try to decode the token as a custom JWT token (without verifying the signature)
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            current_user = decoded_token['sub']  # Extract the user ID (subject) from the custom JWT token
            print("Custom token decoded successfully.")
            return f(current_user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired", "status": "fail", "code": 401}), 401
        except jwt.InvalidTokenError:
            # Step 2: If it's not a valid custom JWT token, try validating as a Google token
            current_user = verify_google_token(token)
            if current_user:
                print("Google token validated successfully.")
                return f(current_user, *args, **kwargs)
            else:
                return jsonify({"message": "Invalid token", "status": "fail", "code": 401}), 401

    return decorated

# Helper function to verify Google ID token
def verify_google_token(token):
    try:
        # Verify the Google token using Google's public keys
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
        
        # Check that the token was issued for this app
        if idinfo['aud'] != GOOGLE_CLIENT_ID:
            raise ValueError('Could not verify audience.')
        
        # Return the user ID from the token
        return idinfo['sub']  # Google user ID
    except ValueError as e:
        print(f"Google token validation error: {str(e)}")
        return None
