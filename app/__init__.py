from gevent import monkey
monkey.patch_all()

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app():
	app = Flask(__name__)
	cors = CORS(
		app, resources={r"/*": {"origins": ["http://127.0.0.1/*", "http://www.algowolf.com/*"]}}, 
		supports_credentials=True,
		allow_headers=["Authorization", "Content-Type", "Accept"]
	)
	sio = SocketIO(app, cors_allowed_origins='*', cors_credentials=True)

	return app, sio

app, sio = create_app()

from app import views