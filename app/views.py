import json
from app import app, sio
from flask import Response
from flask_socketio import emit, join_room, leave_room

@app.route("/")
def index():
	res = { 'message': 'Hello World!' }
	return Response(
		json.dumps(res, indent=2),
		status=200, content_type='application/json'
	)


@sio.on('connect', namespace='/admin')
def connect_admin():
	print('Connected Admin!')
	# Check Auth

	# Refuse connection if not authorized


@sio.on('connect', namespace='/user')
def connect_user():
	print('Connected User!')
	# Check Auth

	# Refuse connection if not authorized


@sio.on('ontick', namespace='/admin')
def ontick_admin(data):
	room = '{}:{}:{}'.format(
		data['broker'], 
		data['item']['product'], 
		data['item']['period']
	)
	emit('ontick', data.get('item'), namespace='/user', room=room)


@sio.on('ontrade', namespace='/admin')
def ontrade_admin(data):
	room = data['strategy_id']
	emit('ontrade', data['item'], namespace='/user', room=room)


@sio.on('ongui', namespace='/admin')
def ongui_admin(data):
	room = data['strategy_id']
	emit('ongui', data['item'], namespace='/user', room=room)


@sio.on('subscribe', namespace='/user')
def subscribe(data):
	join_room('', namespace='/user')


@sio.on('unsubscribe', namespace='/user')
def unsubscribe(data):
	leave_room('', namespace='/user')


