from app import db
from sqlalchemy import PrimaryKeyConstraint, DateTime, Text, Table, Column, Integer, String, ForeignKey, engine
from sqlalchemy import create_engine
from app import engine

    
class UserProfile(db.Model):
    __tablename__ = 'tbl_user_profile_picture'
    ProfileID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.String(255), nullable=False)
    ProfileName = db.Column(db.String(255), nullable=False)
    UploadedAt = db.Column(db.DateTime, server_default=db.func.now())

class Conversation(db.Model):
    __tablename__ = 'tbl_conversation'
    ConversationID = db.Column(Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.String(255), nullable=False)
    StartTime = db.Column(DateTime, server_default=db.func.now())
    EndTime = db.Column(DateTime, nullable=True)

class UserQuery(db.Model):
    __tablename__ = 'tbl_user_query'
    QueryID = db.Column(Integer, primary_key=True, autoincrement=True)
    ConversationID = db.Column(Integer, db.ForeignKey('tbl_conversation.ConversationID'), nullable=False)
    QueryText = db.Column(Text, nullable=False)
    CreatedAt = db.Column(DateTime, server_default=db.func.now())

class BotResponse(db.Model):
    __tablename__ = 'tbl_bot_response'
    ResponseID = db.Column(Integer, primary_key=True, autoincrement=True)
    ConversationID = db.Column(Integer, db.ForeignKey('tbl_conversation.ConversationID'), nullable=False)
    QueryID = db.Column(Integer, db.ForeignKey('tbl_user_query.QueryID'), nullable=True)
    ResponseText = db.Column(Text, nullable=False)
    CreatedAt = db.Column(DateTime, server_default=db.func.now())

