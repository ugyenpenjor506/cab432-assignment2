from app import app
import jwt
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.model.Model import db, UserProfile
import requests
from app.helper.AuthHelper import token_required
import boto3
from werkzeug.utils import secure_filename
from app.helper.SecretManager import get_secrets

# Enable CORS for all routes
CORS(app)

COGNITO_REGION =  get_secrets()['COGNITO_REGION']

# S3 client
s3_client = boto3.client('s3', region_name=COGNITO_REGION)
BUCKET_NAME = 'n1234567-assignment2'

class ProfileController:
    
    @app.route('/upload-profile-picture', methods=['POST'])
    @token_required  # Protect this route with the token
    def upload_profile_picture(current_user):
        # Get the uploaded file from form data
        if 'profile_pic' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        profile_pic = request.files['profile_pic']
        
        if profile_pic.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if profile_pic:
            # Use the current_user (from token) to create a unique file name
            file_name = secure_filename(f"user_{current_user}_profile.jpg")
            try:
                # Generate the presigned URL for uploading to S3
                presigned_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': BUCKET_NAME,
                        'Key': file_name,
                        'ContentType': profile_pic.content_type  # Dynamically get the content type
                    },
                    ExpiresIn=3600  # URL valid for 1 hour
                )

                # Upload the file using the presigned URL
                response = requests.put(presigned_url, data=profile_pic.read(), headers={
                    'Content-Type': profile_pic.content_type
                })
                
                if response.status_code == 200:
                    return jsonify({'message': 'Profile picture uploaded successfully!'}), 200
                else:
                    return jsonify({'error': 'Failed to upload file to S3'}), 500
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': 'No file provided'}), 400

        
    @app.route('/download-profile-picture', methods=['GET'])
    @token_required  # Protect this route with the token
    def download_profile_picture(current_user):
        file_name = secure_filename(f"user_{current_user}_profile.jpg")  # Construct the file name based on user_id
    
        try:
            # Generate the presigned URL for downloading the profile picture from S3
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': BUCKET_NAME,
                    'Key': file_name
                },
                ExpiresIn=3600  # URL valid for 1 hour
            )
            
            return jsonify({'url': presigned_url}), 200
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        
        
