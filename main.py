from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, disconnect
from flask_cors import CORS  # Import CORS
import redis
from app import app
import time  # For

# Enable CORS for all routes
CORS(app)  

# Set up Redis for progress tracking
cache = redis.StrictRedis(host='172.31.3.87', port=6379, decode_responses=True)

# Set up SocketIO for WebSocket communication
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow CORS for all origins. Replace "*" with specific origin if needed.

# Handle new WebSocket connections
@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        join_room(user_id)
        emit('connected', {'message': f'Connected to room {user_id}'})
    else:
        disconnect()

# Handle disconnections
@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.args.get('user_id')
    if user_id:
        emit('disconnected', {'message': 'You have been disconnected.'})

# Handle fetching progress when the client reconnects
@socketio.on('fetch_progress')
def handle_fetch_progress(data):
    task_id = data.get('task_id')
    progress = cache.get(f'progress_{task_id}')
    
    if progress:
        emit('progress_update', {'task_id': task_id, 'progress': progress})
    else:
        emit('progress_update', {'task_id': task_id, 'progress': 'No progress found'})
        
@socketio.on('login_progress')
def handle_login_progress(data):
    task_id = data.get('task_id')
    
    # Simulate login progress updates
    for progress in range(0, 101, 25):  # Simulate progress in increments of 25%
        time.sleep(1)  # Simulate time delay for each step (e.g., processing)
        emit('progress_update', {'task_id': task_id, 'progress': progress}, room=request.sid)
    
    # Optionally, emit the final success or failure message
    emit('progress_complete', {'task_id': task_id, 'status': 'Login successful'}, room=request.sid)

# Main application entry point
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5005, debug=True)
