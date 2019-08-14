from pwnedhub import create_app

app, socketio = create_app()
if __name__ == '__main__':
    socketio.run(app, port=5000)
