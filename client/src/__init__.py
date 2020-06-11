from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__, static_folder='./static')
app.config['SECRET_KEY'] = '46a3aa3658359c95a3fe731050236443'
UPLOAD_FOLDER = './uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# SERVER_IP = '192.168.2.57'
# SERVER_IP = '192.168.43.250'
SERVER_IP = '10.0.0.10'
SERVER_PORT = 65432

from . import routes  # don't touch it!!
