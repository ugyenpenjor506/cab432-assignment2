from app.model.Model import db, Conversation, UserQuery, BotResponse
from flask import jsonify

class DatabaseService:
    def create_conversation(self, user_id):
        try:
            # Create a new conversation instance
            new_conversation = Conversation(UserID=user_id)
            db.session.add(new_conversation)
            db.session.commit()
            
            # Return the newly created conversation
            return new_conversation
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "code": 500, "message": "Error creating conversation", "details": str(e)}), 500
        
    def create_query(self, conversation_id, query_text):
        try:
            # Create a new query instance
            new_query = UserQuery(ConversationID=conversation_id, QueryText = query_text)
            db.session.add(new_query)
            db.session.commit()
            
            # Return the newly created conversation
            return new_query
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "code": 500, "message": "Error creating conversation", "details": str(e)}), 500
        
    def create_response(self, conversation_id, query_id, response_text):
        
        
        try:
            # Create a new query instance
            new_query = BotResponse(ConversationID=conversation_id, QueryID = query_id, ResponseText = response_text)
            db.session.add(new_query)
            db.session.commit()
            
            # Return the newly created response
            return new_query
        except Exception as e:
            db.session.rollback()
            return jsonify({"status": "error", "code": 500, "message": "Error creating response", "details": str(e)}), 500

        
