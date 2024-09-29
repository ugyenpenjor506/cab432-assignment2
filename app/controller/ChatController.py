import redis
from app import app
from app.service.ApiService import ApiService
from app.service.DatabaseService import DatabaseService
from flask import jsonify, request
from flask_cors import CORS
from app.helper.AuthHelper import token_required
from flask_socketio import SocketIO, emit, join_room

# Enable CORS for all routes
CORS(app)

# Set up Redis client
cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Set up SocketIO for WebSockets
socketio = SocketIO(app)

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

        # Start progress tracking in Redis (0% initially)
        task_id = f"chat_{create_conversation.ConversationID}_{create_query.QueryID}"
        cache.set(f'progress_{task_id}', 0)

        # Emit the initial progress (0%) to WebSocket
        socketio.emit('progress_update', {'task_id': task_id, 'progress': 0}, room=user_id)

        # Call the OpenAI API (this could be long-running)
        openai_response = apiService.openai_api(user_input, create_conversation.ConversationID, create_query.QueryID)

        # After the process is done, update the progress to 100% in Redis
        cache.set(f'progress_{task_id}', 100)

        # Emit the final progress (100%) to WebSocket
        socketio.emit('progress_update', {'task_id': task_id, 'progress': 100}, room=user_id)

        # Return the response as JSON, including conversation_id and query_id
        return jsonify({
            "status": "success",
            "code": 200,
            "response": openai_response["response"],
            "cpu_result": openai_response["cpu_result"],
            "conversation_id": create_conversation.ConversationID,  # Include this in the response
            "query_id": create_query.QueryID  # Include this in the response
        }), 200

# Define the `/progress` API to get task progress
@app.route('/progress', methods=['GET'])
@token_required  # Token required to access this route
def get_progress(current_user):
    task_id = request.args.get('task_id')

    if not task_id:
        return jsonify({"error": "Task ID is required"}), 400

    progress = cache.get(f'progress_{task_id}')

    if progress:
        return jsonify({"task_id": task_id, "progress": progress}), 200
    else:
        return jsonify({"error": "No progress found for the task"}), 404


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        join_room(user_id)
        emit('connected', {'message': f'Connected to room {user_id}'})
       
@socketio.on('disconnect')
def handle_disconnect():
    emit('disconnected', {'message': 'You have been disconnected.'})


# Instantiate the controller to ensure the route is registered
apiService = ApiService()
databaseService = DatabaseService()