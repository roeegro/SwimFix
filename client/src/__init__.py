from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mysqldb import MySQL


app = Flask(__name__, static_folder='./static')
app.config['SECRET_KEY'] = '46a3aa3658359c95a3fe731050236443'
UPLOAD_FOLDER = '.\\uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
app.config['MYSQL_HOST'] = '65.19.141.67'
app.config['MYSQL_USER'] = 'lironabr'
app.config['MYSQL_PASSWORD'] = 'h3dChhmg'
app.config['MYSQL_DB'] = 'lironabr_swimming_project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)
# mysql=''
SERVER_IP = '10.0.0.8'
SERVER_PORT = 65432
from . import routes
