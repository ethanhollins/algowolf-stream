import json
import requests
from requests.exceptions import ConnectionError
from app import app, sio
from flask import Response, request
from flask_socketio import (
	ConnectionRefusedError,
	emit, join_room, leave_room
)

connected_brokers = []

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


@sio.on('connect', namespace='/broker')
def connect_broker():
	broker = request.headers.get('Broker')
	print(f'Broker {broker} Connected!')
	if broker not in connected_brokers:
		connected_brokers.append(broker)


@sio.on('disconnect', namespace='/broker')
def disconnect_broker():
	broker = request.headers.get('Broker')
	print(f'Broker {broker} Disconnected!')
	if broker in connected_brokers:
		del connected_brokers[connected_brokers.index(broker)]


@sio.on('ontick', namespace='/admin')
def ontick_admin(data):
	room = '{}:{}:{}'.format(
		data['broker'], 
		data['product'], 
		data['period']
	)

	emit('ontick', data, namespace='/user', room=room, broadcast=True)


@sio.on('ontrade', namespace='/admin')
def ontrade_admin(data):
	room = data['broker_id']
	emit('ontrade', data['item'], namespace='/user', room=room, broadcast=True)


@sio.on('onsessionstatus', namespace='/admin')
def onsessionstatus_admin(data):
	emit('onsessionstatus', data, namespace='/user', broadcast=True)


@sio.on('ongui', namespace='/admin')
def ongui_admin(data):
	room = data['strategy_id']
	emit('ongui', data['item'], namespace='/user', room=room, broadcast=True)


@sio.on('broker_cmd', namespace='/admin')
def broker_cmd(data):
	# print(data)

	if data.get('broker') in connected_brokers:
		emit('broker_cmd', data, namespace='/broker', broadcast=True)
	else:
		emit(
			'broker_res', 
			{
				'error': 'Broker not found.'
			}, 
			namespace='/admin', 
			broadcast=True
		)


@sio.on('broker_res', namespace='/broker')
def broker_res(data):
	emit('broker_res', data, namespace='/admin', broadcast=True)


@sio.on('start', namespace='/admin')
def start_script(data):
	# print(data)
	emit('start', data, namespace='/admin', broadcast=True)


@sio.on('stop', namespace='/admin')
def stop_script(data):
	# print(data)
	emit('stop', data, namespace='/admin', broadcast=True)


@sio.on('subscribe', namespace='/user')
def subscribe(data):
	headers = {
		'Accept': '*/*',
		'Content-Type': 'application/json',
		'Authorization': request.headers.get('Authorization')
	}

	broker_id = data.get('broker_id')
	field = data.get('field')
	items = data.get('items')

	if field == 'ontrade':
		auth_ept = '/authorize'
		try:
			res = requests.post(app.config['API_URL'] + auth_ept, headers=headers)
		except ConnectionError as e:
			raise ConnectionRefusedError('Unable to connect to API')

		if res.status_code == 200:
			join_room(broker_id, namespace='/user')

		else:
			raise ConnectionRefusedError(f'Unauthorized access.')

	elif field == 'ontick':
		if items is None:
			raise ConnectionRefusedError('`items` not found.')

		if isinstance(items, dict):
			chart_ept = f'/v1/strategy/{broker_id}/charts'

			for broker in items:
				try:
					res = requests.post(
						app.config['API_URL'] + chart_ept, 
						headers=headers, 
						data=json.dumps({
							'broker': broker,
							'items': list(items[broker].keys()) 
						})
					)
				except ConnectionError as e:
					raise ConnectionRefusedError('Unable to connect to API')

				status_code = res.status_code
				data = res.json()

				if res.status_code == 200:
					print(f'DATA: {data}')
					for product in data.get('products'):
						if items[broker].get(product) == 'all':
							room = f'{data.get("broker")}:{product}:all'
							print(room)
							join_room(room, namespace='/user')
						else:
							for period in items[broker].get(product):
								room = f'{data.get("broker")}:{product}:{period}'
								print(room)
								join_room(room, namespace='/user')

				else:
					raise ConnectionRefusedError(f'Unauthorized access.')

		else:
			raise ConnectionRefusedError(f'`items` object must be dict.')

	


@sio.on('unsubscribe', namespace='/user')
def unsubscribe(data):
	leave_room('', namespace='/user')


