import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from app.helper.SecretManager import get_secrets
from app.helper.ParameterStore import get_db_host

# Retrieve the db credentials from secret manager using helper function
db_user = get_secrets()['MYSQL_USER']
db_password = get_secrets()['MYSQL_PASSWORD']
db_name = get_secrets()['MYSQL_DATABASE']

 # Retrieve the db host from Parameter Store using the helper function
db_host = get_db_host()

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
