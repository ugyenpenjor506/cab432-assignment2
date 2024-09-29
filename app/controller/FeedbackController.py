from flask import request, jsonify
import boto3
import uuid
from datetime import datetime
from app import app
from app.helper.SecretManager import get_secrets
from app.helper.AuthHelper import token_required

COGNITO_REGION =  get_secrets()['COGNITO_REGION']

# Initialize DynamoDB resource using boto3
dynamodb = boto3.resource('dynamodb', region_name=COGNITO_REGION)

# Connect to the Feedback table
table = dynamodb.Table('Feedback')

class FeedbackContoller:

    @app.route('/submit-feedback', methods=['POST'])
    @token_required
    def submit_feedback():
        data = request.get_json()  # Expecting JSON data

        # Extract user feedback from the request
        user_id = data.get('UserID')
        rating = data.get('Rating')
        comments = data.get('Comments')

        # Basic validation
        if not user_id or not rating or not comments:
            return jsonify({'error': 'UserID, Rating, and Comments are required'}), 400

        # Generate a unique FeedbackID
        feedback_id = str(uuid.uuid4())

        # Insert feedback into DynamoDB
        try:
            table.put_item(
                Item={
                    'FeedbackID': feedback_id,
                    'UserID': user_id,
                    'Rating': rating,
                    'Comments': comments,
                    'Timestamp': datetime.utcnow().isoformat()  # Store the current timestamp
                }
            )
            return jsonify({'message': 'Feedback submitted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        

@app.route('/get-all-feedback', methods=['GET'])
@token_required
def get_all_feedback():
    try:
        feedback_items = []
        response = table.scan()

        feedback_items.extend(response.get('Items', []))

        # Check if there are more items to scan (pagination)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            feedback_items.extend(response.get('Items', []))

        if not feedback_items:
            return jsonify({'message': 'No feedback found'}), 404

        return jsonify({'feedback': feedback_items}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
