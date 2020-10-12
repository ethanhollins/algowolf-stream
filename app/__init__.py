from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
sio = SocketIO(app)

from app import views