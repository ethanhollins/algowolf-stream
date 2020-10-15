from gevent import monkey
monkey.patch_all()

import os
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

def create_app(test_config=None):
	
	instance_path = os.path.join(os.path.abspath(os.getcwd()), 'instance')
	app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)

	app.config.from_mapping(
		SECRET_KEY='dev',
		BROKERS=os.path.join(app.instance_path, 'brokers.json')
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# Ensure the instance folder exists
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	assert 'API_URL' in app.config, 'API_URL not found.'
	assert 'ORIGINS' in app.config, 'ORIGINS not found.'

	cors = CORS(
		app, resources={r"/*": {"origins": app.config['ORIGINS']}}, 
		supports_credentials=True,
		allow_headers=["Authorization", "Content-Type", "Accept"]
	)

	if 'DEBUG' in app.config:
		app.debug = app.config['DEBUG']

	sio = SocketIO(app, cors_allowed_origins='*', cors_credentials=True)

	return app, sio

app, sio = create_app()

from app import views