from pwnedhub import create_app

app, socketio = create_app()
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
