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
    @token_required  # Protect this route with the token
    def chatQuery(current_user):
        
        data = request.get_json()  # Extract the request body data

        # Get user_id from the request body or use the current_user from the token
        user_id = current_user

        if not user_id:
            return jsonify({"status": "error", "code": 400, "message": "User ID is required"}), 400

        # Now use the user_id to create a conversation
        create_conversation = databaseService.create_conversation(user_id)
        
        if create_conversation is None:
            return jsonify({"status": "error", "code": 500, "message": "Failed to create conversation"}), 500

        # Safely access ConversationID
        user_input = data.get("query")  # Extract the user's query from the request body
        
        if not user_input:
            return jsonify({"status": "error", "code": 400, "message": "No query provided"}), 400

        # Create the query in the database with the ConversationID and user input
        create_query = databaseService.create_query(create_conversation.ConversationID, user_input)

        # Call the OpenAI API with user input, ConversationID, and QueryID
        return apiService.openai_api(user_input, create_conversation.ConversationID, create_query.QueryID)

   

# Instantiate the controller to ensure the route is registered
apiService = ApiService()
databaseService = DatabaseService()
