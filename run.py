from app import app, sio

if __name__ == '__main__':
	sio.run(app, port=3001)
