from functools import wraps
from flask import request, jsonify
import jwt

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
            # Decode the token (without verifying the signature for now)
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            current_user = decoded_token['sub']  # Extract the user ID (subject) from the token
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired", "status": "fail", "code": 401}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token", "status": "fail", "code": 401}), 401
        
        # Pass the current user information to the wrapped function
        return f(current_user, *args, **kwargs)
    
    return decorated
