import json
import requests
from app import app, sio
from flask import Response, request
from flask_socketio import (
	ConnectionRefusedError,
	emit, join_room, leave_room
)

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
	headers = {
		'Accept': '*/*',
		'Content-Type': 'application/json',
		'Authorization': request.headers.get('Authorization')
	}

	strategy_id = data.get('strategy_id')
	field = data.get('field')
	items = data.get('items')

	if field == 'ontrade':
		auth_ept = '/authorize'
		res = requests.post(app.config['API_URL'] + auth_ept, headers=headers)

		if res.status_code == 200:
			join_room(strategy_id, namespace='/user')

		else:
			raise ConnectionRefusedError(f'Unauthorized access.')

	elif field == 'ontick':
		if items is None:
			raise ConnectionRefusedError('`items` not found.')

		if isinstance(items, dict):
			chart_ept = f'/v1/strategy/{strategy_id}/charts'
			res = requests.post(
				app.config['API_URL'] + chart_ept, 
				headers=headers, 
				data=json.dumps({ 'items': list(items.keys()) })
			)

			status_code = res.status_code
			data = res.json()

			if res.status_code == 200:
				print(f'DATA: {data}')
				for product in data.get('products'):
					for period in items.get(product):
						room = f'{data.get("broker")}:{product}:{period}'
						join_room(room, namespace='/user')

			else:
				raise ConnectionRefusedError(f'Unauthorized access.')

		else:
			raise ConnectionRefusedError(f'`items` object must be dict.')

	


@sio.on('unsubscribe', namespace='/user')
def unsubscribe(data):
	leave_room('', namespace='/user')


