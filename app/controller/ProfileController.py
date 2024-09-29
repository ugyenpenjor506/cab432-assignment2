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
    
    @app.route('/upload-profile-picture/<int:user_id>', methods=['POST'])
    @token_required  # Protect this route with the token
    def upload_profile_picture(user_id):
        profile_pic = request.files['profile_pic']  # Get the uploaded file from form data
        
        if profile_pic:
            file_name = secure_filename(f"user_{user_id}_profile.jpg")
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
                files = {'file': (file_name, profile_pic.read(), profile_pic.content_type)}
                response = requests.put(presigned_url, data=files['file'][1], headers={
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
        
        
    @app.route('/download-profile-picture/<int:user_id>', methods=['GET'])
    @token_required  # Protect this route with the token
    def download_profile_picture(user_id):
        file_name = secure_filename(f"user_{user_id}_profile.jpg")  # Construct the file name based on user_id
    
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

        
        
