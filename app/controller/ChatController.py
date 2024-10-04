from app import app
from app.service.ApiService import ApiService
from app.service.DatabaseService import DatabaseService
from flask import jsonify, request
from flask_cors import CORS
from app.helper.AuthHelper import token_required

# Enable CORS for all routes
CORS(app)

class ChatController:
    
    @app.route('/chat', methods=['POST'], strict_slashes=False)
    @token_required  # Protect this route with either Google or custom token
    def chatQuery(current_user):
        data = request.get_json()  # Extract the request body data

        user_id = current_user  # The user ID from the token (Google or custom)

        if not user_id:
            return jsonify({
                "status": "error", 
                "code": 400, 
                "message": "User ID is required"
            }), 400

        # Use the user_id to create a conversation
        create_conversation = databaseService.create_conversation(user_id)
        
        if create_conversation is None:
            return jsonify({
                "status": "error", 
                "code": 500, 
                "message": "Failed to create conversation"
            }), 500

        user_input = data.get("query")  # Extract the user's query from the request body
        
        if not user_input:
            return jsonify({
                "status": "error", 
                "code": 400, 
                "message": "No query provided"
            }), 400

        # Create the query in the database with the ConversationID and user input
        create_query = databaseService.create_query(create_conversation.ConversationID, user_input)

        # Call the OpenAI API (this could be long-running)
        openai_response = apiService.openai_api(user_input, create_conversation.ConversationID, create_query.QueryID)

        # Check if 'response' exists in the OpenAI API response
        if "response" not in openai_response:
            return jsonify({
                "status": "error", 
                "code": 500, 
                "message": f"Unexpected OpenAI API response format: {openai_response}"
            }), 500

        # Return the response as JSON, including conversation_id and query_id
        return jsonify({
            "status": "success",
            "code": 200,
            "response": openai_response["response"],
            "cpu_result": openai_response.get("cpu_result", None),  # Use .get() to handle missing keys
            "conversation_id": create_conversation.ConversationID,  # Include this in the response
            "query_id": create_query.QueryID  # Include this in the response
        }), 200

# Instantiate the controller to ensure the route is registered
apiService = ApiService()
databaseService = DatabaseService()
