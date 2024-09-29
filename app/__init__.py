import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from dotenv import load_dotenv
load_dotenv()

# Get database connection details from environment variables
db_user = os.getenv('MYSQL_USER')
db_password = os.getenv('MYSQL_PASSWORD')
db_host = os.getenv('MYSQL_HOST')
db_name = os.getenv('MYSQL_DATABASE')


con = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:3306/{db_name}"

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = con
db = SQLAlchemy(app)

engine = create_engine(con, echo=True)
if not database_exists(engine.url):
    create_database(engine.url)
else:
    engine.connect()

from app.controller.ChatController import ChatController
from app.controller.UserController import UserController
from app.controller.ProfileController import ProfileController
from app.controller.FeedbackController import FeedbackContoller
